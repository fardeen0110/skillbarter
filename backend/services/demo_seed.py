from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import auth, models
from .notifications import create_notification
from .social import recalculate_rating
from .users import ensure_profile, ensure_skill_catalog, set_user_skills

DEMO_USERS = [
    {
        "name": "Demo User",
        "email": "demo@skillbarter.com",
        "password": "demo123",
        "city": "Bengaluru",
        "bio": "Product-minded builder exploring sharper workflows through reciprocal skill swaps.",
        "availability": "Weeknights, Saturday mornings",
        "experience": "advanced",
        "offered": ["React", "Product Strategy", "Pitch Decks"],
        "wanted": ["AI Workflow Design", "Growth Marketing", "Video Editing"],
        "rating": (4.8, 6),
    },
    {
        "name": "Aarav Mehta",
        "email": "aarav@skillbarter.demo",
        "password": "demo123",
        "city": "Mumbai",
        "bio": "Frontend engineer who loves helping founders turn rough ideas into polished interfaces.",
        "availability": "Weeknights, Sunday afternoons",
        "experience": "advanced",
        "offered": ["React", "UI Design"],
        "wanted": ["SEO", "Public Speaking"],
        "rating": (4.9, 11),
    },
    {
        "name": "Maya Chen",
        "email": "maya@skillbarter.demo",
        "password": "demo123",
        "city": "Singapore",
        "bio": "Brand strategist pairing crisp positioning with practical startup storytelling.",
        "availability": "Mornings, Fridays",
        "experience": "expert",
        "offered": ["Content Writing", "Growth Marketing", "Pitch Decks"],
        "wanted": ["SQL", "No-Code Automation"],
        "rating": (4.7, 9),
    },
    {
        "name": "Rohan Iyer",
        "email": "rohan@skillbarter.demo",
        "password": "demo123",
        "city": "Pune",
        "bio": "Data analyst translating messy spreadsheets into usable decisions for operators.",
        "availability": "Weekdays after 7pm",
        "experience": "advanced",
        "offered": ["Data Analysis", "SQL"],
        "wanted": ["Public Speaking", "Product Strategy"],
        "rating": (4.6, 8),
    },
    {
        "name": "Elena Garcia",
        "email": "elena@skillbarter.demo",
        "password": "demo123",
        "city": "Barcelona",
        "bio": "Creative lead helping small teams ship visuals that feel trustworthy and premium.",
        "availability": "Flexible afternoons",
        "experience": "expert",
        "offered": ["Graphic Design", "Motion Design"],
        "wanted": ["React", "AI Workflow Design"],
        "rating": (4.9, 14),
    },
    {
        "name": "Noah Williams",
        "email": "noah@skillbarter.demo",
        "password": "demo123",
        "city": "Austin",
        "bio": "Growth operator focused on experiments, funnels, and sustainable acquisition loops.",
        "availability": "Early mornings, weekends",
        "experience": "advanced",
        "offered": ["Growth Marketing", "SEO"],
        "wanted": ["Figma", "Video Editing"],
        "rating": (4.5, 7),
    },
    {
        "name": "Priya Nair",
        "email": "priya@skillbarter.demo",
        "password": "demo123",
        "city": "Hyderabad",
        "bio": "Operations lead building calmer systems, cleaner handoffs, and stronger team habits.",
        "availability": "Weeknights",
        "experience": "advanced",
        "offered": ["Project Management", "Career Coaching"],
        "wanted": ["React", "Content Writing"],
        "rating": (4.8, 10),
    },
    {
        "name": "Liam Patel",
        "email": "liam@skillbarter.demo",
        "password": "demo123",
        "city": "London",
        "bio": "Technical founder obsessed with automations that remove repetitive work.",
        "availability": "Tuesdays, Thursdays, weekends",
        "experience": "expert",
        "offered": ["No-Code Automation", "AI Workflow Design"],
        "wanted": ["Product Strategy", "Public Speaking"],
        "rating": (4.9, 13),
    },
    {
        "name": "Sophia Kim",
        "email": "sophia@skillbarter.demo",
        "password": "demo123",
        "city": "Seoul",
        "bio": "Design systems specialist who enjoys turning visual chaos into scalable product patterns.",
        "availability": "Late evenings",
        "experience": "advanced",
        "offered": ["Figma", "UI Design"],
        "wanted": ["Node.js", "Data Analysis"],
        "rating": (4.7, 12),
    },
    {
        "name": "Daniel Okafor",
        "email": "daniel@skillbarter.demo",
        "password": "demo123",
        "city": "Lagos",
        "bio": "Story-first marketer helping products sound human, clear, and differentiated.",
        "availability": "Mon/Wed/Fri evenings",
        "experience": "advanced",
        "offered": ["Content Writing", "Public Speaking"],
        "wanted": ["SQL", "React"],
        "rating": (4.6, 9),
    },
    {
        "name": "Ishita Rao",
        "email": "ishita@skillbarter.demo",
        "password": "demo123",
        "city": "Chennai",
        "bio": "Full-stack builder with a soft spot for mentoring people through intimidating technical problems.",
        "availability": "Saturday afternoons, Sunday evenings",
        "experience": "expert",
        "offered": ["Python", "Node.js"],
        "wanted": ["Graphic Design", "Pitch Decks"],
        "rating": (4.8, 15),
    },
    {
        "name": "Mateo Silva",
        "email": "mateo@skillbarter.demo",
        "password": "demo123",
        "city": "Sao Paulo",
        "bio": "Editor and motion designer helping technical ideas feel dynamic and understandable.",
        "availability": "Flexible weekends",
        "experience": "advanced",
        "offered": ["Video Editing", "Motion Design"],
        "wanted": ["SEO", "Project Management"],
        "rating": (4.7, 8),
    },
    {
        "name": "Zara Ali",
        "email": "zara@skillbarter.demo",
        "password": "demo123",
        "city": "Dubai",
        "bio": "Presentation coach helping operators sound concise, credible, and confident.",
        "availability": "Mornings",
        "experience": "expert",
        "offered": ["Public Speaking", "Career Coaching"],
        "wanted": ["AI Workflow Design", "React"],
        "rating": (4.9, 16),
    },
    {
        "name": "Victor Hansen",
        "email": "victor@skillbarter.demo",
        "password": "demo123",
        "city": "Copenhagen",
        "bio": "Analytics consultant simplifying instrumentation and reporting for small product teams.",
        "availability": "Weekday mornings",
        "experience": "advanced",
        "offered": ["SQL", "Data Analysis"],
        "wanted": ["Growth Marketing", "Graphic Design"],
        "rating": (4.5, 6),
    },
    {
        "name": "Ananya Das",
        "email": "ananya@skillbarter.demo",
        "password": "demo123",
        "city": "Delhi",
        "bio": "Product generalist who enjoys structuring messy initiatives into clear execution plans.",
        "availability": "Tuesday and Thursday evenings",
        "experience": "advanced",
        "offered": ["Product Strategy", "Project Management"],
        "wanted": ["Motion Design", "SEO"],
        "rating": (4.8, 11),
    },
    {
        "name": "Lucas Brown",
        "email": "lucas@skillbarter.demo",
        "password": "demo123",
        "city": "Toronto",
        "bio": "Backend-focused engineer helping non-technical teams understand what good software tradeoffs look like.",
        "availability": "Weekends, late evenings",
        "experience": "expert",
        "offered": ["Python", "Node.js", "SQL"],
        "wanted": ["UI Design", "Content Writing"],
        "rating": (4.7, 10),
    },
]


def _now_minus(*, days: int = 0, hours: int = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days, hours=hours)


def _get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.execute(select(models.User).where(models.User.email == email.lower())).scalar_one_or_none()


def _ensure_user(db: Session, definition: dict, index: int) -> models.User:
    user = _get_user_by_email(db, definition["email"])
    if not user:
        user = models.User(
            name=definition["name"],
            email=definition["email"].lower(),
            password_hash=auth.hash_password(definition["password"]),
            is_verified=True,
            is_admin=False,
            last_active_at=_now_minus(days=index % 5, hours=(index * 3) % 20),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    profile = ensure_profile(db, user)
    user.password_hash = auth.hash_password(definition["password"])
    profile.bio = definition["bio"]
    profile.city = definition["city"]
    profile.availability = definition["availability"]
    profile.experience_level = definition["experience"]
    profile.linkedin_url = f"https://linkedin.com/in/{definition['name'].lower().replace(' ', '-')}"
    profile.website_url = f"https://{definition['email'].split('@')[0]}.demo.skillbarter.local"
    profile.x_url = f"https://x.com/{definition['email'].split('@')[0]}"
    profile.rating_average = definition["rating"][0]
    profile.rating_count = definition["rating"][1]

    user.name = definition["name"]
    user.is_verified = True
    user.is_admin = False
    user.last_active_at = _now_minus(days=index % 5, hours=(index * 3) % 20)

    db.add(user)
    db.add(profile)
    db.commit()
    db.refresh(user)

    set_user_skills(db, user, offered=definition["offered"], wanted=definition["wanted"])
    db.refresh(user)
    return user


def _ensure_friend_request(db: Session, sender_id: int, receiver_id: int, status: str) -> models.FriendRequest:
    existing = db.execute(
        select(models.FriendRequest).where(
            models.FriendRequest.sender_id == sender_id,
            models.FriendRequest.receiver_id == receiver_id,
        )
    ).scalar_one_or_none()
    if existing:
        existing.status = status
        existing.updated_at = datetime.now(timezone.utc)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    request = models.FriendRequest(
        sender_id=sender_id,
        receiver_id=receiver_id,
        status=status,
        created_at=_now_minus(days=3),
        updated_at=_now_minus(days=1),
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def _ensure_follow(db: Session, follower_id: int, followed_id: int) -> None:
    existing = db.execute(
        select(models.Follow).where(
            models.Follow.follower_id == follower_id,
            models.Follow.followed_id == followed_id,
        )
    ).scalar_one_or_none()
    if existing:
        return
    db.add(models.Follow(follower_id=follower_id, followed_id=followed_id, created_at=_now_minus(days=2)))
    db.commit()


def _ensure_review(db: Session, reviewer_id: int, reviewee_id: int, rating: int, comment: str, endorsement: str) -> None:
    existing = db.execute(
        select(models.Review).where(
            models.Review.reviewer_id == reviewer_id,
            models.Review.reviewee_id == reviewee_id,
        )
    ).scalar_one_or_none()
    if existing:
        return
    db.add(
        models.Review(
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            rating=rating,
            comment=comment,
            endorsement=endorsement,
            created_at=_now_minus(days=4),
        )
    )
    db.commit()
    recalculate_rating(db, reviewee_id)


def _ensure_notification(db: Session, user_id: int, title: str, body: str, notification_type: str, link_url: str) -> None:
    existing = db.execute(
        select(models.Notification).where(
            models.Notification.user_id == user_id,
            models.Notification.title == title,
        )
    ).scalar_one_or_none()
    if existing:
        return
    create_notification(
        db,
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        body=body,
        link_url=link_url,
    )


def _ensure_message(db: Session, sender_id: int, receiver_id: int, content: str, *, days: int, read: bool) -> None:
    existing = db.execute(
        select(models.Message).where(
            models.Message.sender_id == sender_id,
            models.Message.receiver_id == receiver_id,
            models.Message.content == content,
        )
    ).scalar_one_or_none()
    if existing:
        return
    created_at = _now_minus(days=days, hours=sender_id % 5)
    message = models.Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        message_type="text",
        created_at=created_at,
        delivered_at=created_at + timedelta(minutes=1),
        read_at=(created_at + timedelta(hours=4)) if read else None,
    )
    db.add(message)
    db.commit()


def _ensure_learning_request(
    db: Session,
    *,
    creator_id: int,
    skill_id: int,
    title: str,
    description: str,
    city: str,
    availability: str,
) -> models.LearningRequest:
    existing = db.execute(
        select(models.LearningRequest).where(
            models.LearningRequest.creator_id == creator_id,
            models.LearningRequest.title == title,
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    item = models.LearningRequest(
        creator_id=creator_id,
        skill_id=skill_id,
        title=title,
        description=description,
        city=city,
        availability=availability,
        status="open",
        created_at=_now_minus(days=5),
        updated_at=_now_minus(days=2),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _ensure_application(db: Session, request_id: int, applicant_id: int, message: str) -> None:
    existing = db.execute(
        select(models.LearningRequestApplication).where(
            models.LearningRequestApplication.request_id == request_id,
            models.LearningRequestApplication.applicant_id == applicant_id,
        )
    ).scalar_one_or_none()
    if existing:
        return
    db.add(
        models.LearningRequestApplication(
            request_id=request_id,
            applicant_id=applicant_id,
            message=message,
            status="pending",
            created_at=_now_minus(days=1),
            updated_at=_now_minus(days=1),
        )
    )
    db.commit()


def seed_demo_data(db: Session) -> None:
    ensure_skill_catalog(db)
    users = [_ensure_user(db, definition, index) for index, definition in enumerate(DEMO_USERS)]
    users_by_email = {user.email: user for user in users}
    demo_user = users_by_email["demo@skillbarter.com"]

    accepted_friends = [
        users_by_email["aarav@skillbarter.demo"],
        users_by_email["maya@skillbarter.demo"],
        users_by_email["liam@skillbarter.demo"],
        users_by_email["priya@skillbarter.demo"],
        users_by_email["zara@skillbarter.demo"],
    ]
    pending_incoming = [
        users_by_email["elena@skillbarter.demo"],
        users_by_email["noah@skillbarter.demo"],
    ]
    pending_outgoing = [users_by_email["rohan@skillbarter.demo"]]

    for friend in accepted_friends:
        _ensure_friend_request(db, friend.id, demo_user.id, "accepted")
        _ensure_follow(db, demo_user.id, friend.id)
        _ensure_follow(db, friend.id, demo_user.id)

    for sender in pending_incoming:
        _ensure_friend_request(db, sender.id, demo_user.id, "pending")

    for receiver in pending_outgoing:
        _ensure_friend_request(db, demo_user.id, receiver.id, "pending")

    _ensure_review(db, accepted_friends[0].id, demo_user.id, 5, "Very thoughtful barter partner with clear asks.", "Great collaborator")
    _ensure_review(db, accepted_friends[1].id, demo_user.id, 5, "Came prepared and made the session useful immediately.", "Sharp product thinking")
    _ensure_review(db, demo_user.id, accepted_friends[2].id, 5, "Excellent automation walkthrough with practical examples.", "Automation expert")

    message_pairs = [
        (accepted_friends[0], "Loved your React teardown. Want to swap on growth experiments next week?", True),
        (demo_user, "Absolutely. I can share the onboarding hypotheses I’ve been testing.", True),
        (accepted_friends[1], "I reviewed your deck and left a few narrative suggestions.", False),
        (demo_user, "Perfect. I’m also curious how you’d tighten the opening headline.", False),
    ]
    for offset, (sender, content, read) in enumerate(message_pairs, start=1):
        receiver = demo_user if sender.id != demo_user.id else accepted_friends[0]
        if offset > 2:
            receiver = demo_user if sender.id != demo_user.id else accepted_friends[1]
        _ensure_message(db, sender.id, receiver.id, content, days=offset, read=read)

    skill_lookup = {
        skill.name: skill
        for skill in db.execute(select(models.Skill)).scalars()
    }
    requests = [
        (
            accepted_friends[0].id,
            skill_lookup["SEO"].id,
            "Need a fast SEO review for a portfolio site",
            "Looking for a practical 30-minute audit and a shortlist of high-impact fixes.",
            "Mumbai",
            "Sunday mornings",
        ),
        (
            accepted_friends[1].id,
            skill_lookup["No-Code Automation"].id,
            "Want help automating lead follow-up",
            "I need a lightweight Zapier-style workflow for follow-up after discovery calls.",
            "Singapore",
            "Friday afternoons",
        ),
        (
            demo_user.id,
            skill_lookup["Video Editing"].id,
            "Seeking help cutting a short launch demo",
            "Need a crisp 60-second product walkthrough video for a portfolio case study.",
            "Bengaluru",
            "Saturday mornings",
        ),
        (
            users_by_email["ananya@skillbarter.demo"].id,
            skill_lookup["React"].id,
            "Need feedback on a component architecture",
            "Looking for someone to review tradeoffs in a growing frontend codebase.",
            "Delhi",
            "Weeknights",
        ),
    ]
    created_requests = [
        _ensure_learning_request(
            db,
            creator_id=creator_id,
            skill_id=skill_id,
            title=title,
            description=description,
            city=city,
            availability=availability,
        )
        for creator_id, skill_id, title, description, city, availability in requests
    ]

    _ensure_application(
        db,
        created_requests[0].id,
        demo_user.id,
        "I can turn this into a concise checklist and quick keyword cleanup plan.",
    )
    _ensure_application(
        db,
        created_requests[1].id,
        accepted_friends[2].id,
        "I’ve built similar workflows and can help map the triggers clearly.",
    )

    notifications = [
        ("New demo match available", "Aarav and Liam are both strong fits for your current goals.", "match", "/matches"),
        ("Pending requests waiting", "You have two inbound connection requests to review.", "friend_request", "/chat"),
        ("Marketplace is active", "Your video editing request already has one interested collaborator.", "marketplace", "/marketplace"),
    ]
    for title, body, notification_type, link_url in notifications:
        _ensure_notification(db, demo_user.id, title, body, notification_type, link_url)

import random

PASSAGES = {
    "easy": [
        "Small steps every day can lead to big changes in your life.",
        "The bright sun warmed the quiet park as birds sang in the trees.",
        "A calm mind helps you learn new skills and solve hard problems.",
        "Fresh bread, cool rain, and a warm cup made the morning feel special.",
        "Practice with patience, and your speed will grow one day at a time.",
    ],
    "medium": [
        "Technology becomes useful when thoughtful people apply it to everyday challenges and create tools that are simple, reliable, and welcoming to everyone.",
        "Walking beside the lake at sunset, Maya noticed how the changing colors reflected across the water and inspired a new idea for her painting.",
        "Good communication depends on listening carefully, choosing words clearly, and giving others enough time to share their perspective without interruption.",
        "The small library offered a quiet refuge where visitors could explore distant worlds, discover new interests, and exchange recommendations with friendly readers.",
        "Creative projects often begin with uncertainty, but steady effort and constructive feedback can transform an uncertain idea into something meaningful.",
    ],
    "hard": [
        "Asynchronous systems demand disciplined architecture: state must be observable, boundaries must remain predictable, and failure recovery should preserve consistency without sacrificing responsiveness.",
        "Although quantum mechanics challenges conventional intuition, its mathematical framework has transformed scientific inquiry and enabled technologies that influence modern computing and communication.",
        "The expedition's meticulous observations challenged several longstanding assumptions, prompting researchers to reconsider whether environmental adaptation or genetic diversity had produced the remarkable outcome.",
        "When sophisticated applications scale unpredictably, developers must measure bottlenecks precisely, eliminate unnecessary complexity, and balance maintainability against performance requirements.",
        "Psychologists emphasize metacognition—the awareness of one's own thought processes—because deliberate reflection can reveal hidden assumptions and improve decision-making under pressure.",
    ],
}


def get_random_passage(difficulty="easy"):
    difficulty = difficulty.lower() if difficulty else "easy"
    if difficulty not in PASSAGES:
        raise ValueError("Difficulty must be easy, medium, or hard")
    return random.choice(PASSAGES[difficulty])

from dataclasses import dataclass

@dataclass
class SafetyCheckResult:
    is_safe: bool
    requires_urgent_care: bool
    urgent_message: str | None
    flag_matched: str | None


RED_FLAGS = [
    ("bleeding for more than", "heavy_bleeding_duration"),
    ("soaking pad every hour", "heavy_bleeding_rate"),
    ("soaking through pad", "heavy_bleeding_rate"),
    ("cant stop bleeding", "heavy_bleeding_duration"),
    ("cannot stop bleeding", "heavy_bleeding_duration"),
    ("blood clots", "clots"),
    ("large clots", "clots"),
    ("no period for 3 months", "amenorrhea"),
    ("missed period for 3", "amenorrhea"),
    ("no period for three", "amenorrhea"),
    ("haven't had period", "amenorrhea"),
    ("havent had period", "amenorrhea"),
    ("pregnant", "pregnancy_concern"),
    ("fainting", "severe_symptom"),
    ("fainted", "severe_symptom"),
    ("passing out", "severe_symptom"),
    ("very dizzy", "severe_symptom"),
    ("severe pain", "severe_pain"),
    ("unbearable pain", "severe_pain"),
    ("pain is unbearable", "severe_pain"),
    ("cant move because of pain", "severe_pain"),
    ("fever and pelvic", "infection"),
    ("pelvic pain and fever", "infection"),
    ("unusual discharge", "infection"),
    ("bleeding after menopause", "post_menopausal_bleeding"),
    ("bleeding after 50", "post_menopausal_bleeding"),
    ("haven't had period in a year", "post_menopausal_bleeding"),
    ("suicide", "mental_health_crisis"),
    ("want to die", "mental_health_crisis"),
    ("hurt myself", "mental_health_crisis"),
]

URGENT_MESSAGES = {
    "heavy_bleeding_duration": (
        "This sounds like heavy bleeding that needs medical attention soon. "
        "Please visit a doctor or clinic today. If you are feeling very weak, "
        "dizzy, or faint, go to the nearest emergency room immediately."
    ),
    "heavy_bleeding_rate": (
        "Soaking through pads very quickly is a sign of heavy bleeding. "
        "Please see a doctor today. If you feel very weak or faint, "
        "go to the emergency room immediately."
    ),
    "clots": (
        "Passing large blood clots may need medical evaluation. "
        "Please consult a doctor, especially if this is new or unusual for you."
    ),
    "amenorrhea": (
        "Missing periods for 3 or more months needs medical evaluation. "
        "Please visit a doctor to understand the cause. "
        "This is especially important to rule out pregnancy or hormonal conditions."
    ),
    "pregnancy_concern": (
        "If you think you might be pregnant, please take a pregnancy test "
        "and consult a doctor as soon as possible for proper care."
    ),
    "severe_symptom": (
        "Fainting or severe dizziness during your period needs immediate attention. "
        "Please go to the nearest emergency room or call for help immediately."
    ),
    "severe_pain": (
        "Severe or unbearable pain is not normal and needs medical attention. "
        "Please visit a doctor today. If the pain is extreme, "
        "go to the emergency room."
    ),
    "infection": (
        "Fever combined with pelvic pain or unusual discharge may indicate an infection. "
        "Please see a doctor today — infections need prompt treatment."
    ),
    "post_menopausal_bleeding": (
        "Any bleeding after menopause needs immediate medical evaluation. "
        "Please see a doctor as soon as possible — do not wait."
    ),
    "mental_health_crisis": (
        "It sounds like you may be going through a very difficult time. "
        "Please reach out to someone you trust right now. "
        "In India, you can call iCall at 9152987821 for free mental health support."
    ),
}

DEFAULT_URGENT_MESSAGE = (
    "This sounds like it may need medical attention. "
    "Please consult a doctor as soon as possible."
)


class SafetyFilter:
    def check(self, question: str) -> SafetyCheckResult:
        question_lower = question.lower().strip()
        
        for phrase, flag_type in RED_FLAGS:
            if phrase in question_lower:
                message = URGENT_MESSAGES.get(flag_type, DEFAULT_URGENT_MESSAGE)
                return SafetyCheckResult(
                    is_safe=False,
                    requires_urgent_care=True,
                    urgent_message=message,
                    flag_matched=flag_type,
                )
        
        return SafetyCheckResult(
            is_safe=True,
            requires_urgent_care=False,
            urgent_message=None,
            flag_matched=None,
        )


safety_filter = SafetyFilter()

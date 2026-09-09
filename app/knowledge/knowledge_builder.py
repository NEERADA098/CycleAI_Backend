import chromadb
from chromadb.utils import embedding_functions
import uuid

MEDICAL_KNOWLEDGE = [
    {
        "id": "menstrual_cycle_normal",
        "content": """Normal menstrual cycle length is between 21 and 35 days, 
        measured from the first day of one period to the first day of the next. 
        Normal period duration is 2 to 7 days. Average cycle length is 28 days 
        but varies between individuals. A cycle is considered irregular when it 
        consistently falls outside the 21-35 day range or varies by more than 
        7 days between cycles.""",
        "category": "cycle_basics"
    },
    {
        "id": "menarche_normal",
        "content": """The first menstrual period (menarche) normally occurs between 
        ages 10 and 14, with an average age of 12 years. During the first 1-2 years 
        after menarche, irregular periods are completely normal and expected as the 
        body establishes its hormonal cycle. Young girls should not be alarmed by 
        irregular periods in the first two years after their first period.""",
        "category": "cycle_basics"
    },
    {
        "id": "dysmenorrhea_types",
        "content": """There are two types of period pain. Spasmodic dysmenorrhea is 
        pain occurring only on the first or second day of the period — this is normal 
        and common. Congestive dysmenorrhea is pain that starts before the period begins 
        and continues for 4 to 6 days — this is NOT normal and may indicate conditions 
        like endometriosis or fibroid uterus. If pain starts before your period and 
        lasts more than 2 days into the period, consult a doctor.""",
        "category": "pain"
    },
    {
        "id": "heavy_bleeding",
        "content": """Heavy menstrual bleeding is defined as needing to change pads 
        every 2 hours or less. Passing large blood clots is also a sign of heavy 
        bleeding. Normal period flow allows pad changes every 4-6 hours. If you are 
        soaking through pads in under 2 hours, or passing clots larger than a coin, 
        this requires medical attention. Heavy bleeding combined with dizziness or 
        extreme fatigue is a sign of possible anemia and needs urgent evaluation.""",
        "category": "bleeding"
    },
    {
        "id": "pcos_indicators",
        "content": """From cycle tracking data alone, PCOS (Polycystic Ovary Syndrome) 
        may be suspected when cycles are consistently longer than 35-40 days, or when 
        periods are very irregular over 6 or more cycles. Additional indicators visible 
        without tests include: facial hair growth (hirsutism), persistent acne especially 
        on the jaw and chin, unexplained weight gain, and darkening of skin in neck or 
        armpit areas (acanthosis nigricans). PCOS diagnosis requires ultrasound and 
        blood tests — an app cannot diagnose PCOS.""",
        "category": "conditions"
    },
    {
        "id": "menopause_perimenopause",
        "content": """The average age of menopause in Indian women is 47 years. 
        Menopause is confirmed after 12 consecutive months without a period. 
        Premature menopause occurs before age 40. Perimenopause (the transition 
        period before menopause) commonly involves irregular periods, delayed periods, 
        spotting, hot flashes, excessive sweating, anxiety, and mood changes. 
        These symptoms in a woman approaching 47 are expected and do not indicate 
        a medical problem.""",
        "category": "lifecycle"
    },
    {
        "id": "ovulation_timing",
        "content": """Ovulation occurs approximately 14 days before the next expected 
        period, regardless of cycle length. For a 28-day cycle, ovulation is around 
        day 14. For a 30-day cycle, around day 16. For a 32-day cycle, around day 18. 
        The egg (ovum) remains active for 48-72 hours after ovulation. Tracking 
        ovulation is useful for both family planning and understanding cycle health.""",
        "category": "cycle_basics"
    },
    {
        "id": "thyroid_cycle_connection",
        "content": """Thyroid problems can cause irregular menstrual cycles similar 
        to PCOS. Both conditions may present with irregular cycles and cannot be 
        distinguished from cycle data alone. A thyroid function blood test is 
        required to rule out thyroid problems in someone with irregular cycles. 
        If you have irregular periods, ask your doctor to check both thyroid 
        function and for PCOS.""",
        "category": "conditions"
    },
    {
        "id": "when_to_see_doctor",
        "content": """See a doctor if: periods have not come for 3 or more consecutive 
        months (not pregnant), you need to change pads every 2 hours or less, 
        period pain starts before your period and lasts more than 2 days, 
        you experience severe dizziness or fainting during periods, 
        you notice unusual facial hair growth or skin darkening, 
        your cycles were regular and suddenly become very irregular, 
        or you have not had your first period by age 15.""",
        "category": "safety"
    },
    {
        "id": "pain_management",
        "content": """For normal period cramps (spasmodic dysmenorrhea), safe home 
        remedies include applying a warm cloth or hot water bottle to the lower 
        abdomen, gentle walking or light exercise, and staying hydrated. 
        Common pain medications like ibuprofen or paracetamol taken at the first 
        sign of cramps are safe and effective. If pain is severe enough to prevent 
        daily activities, or if over-the-counter medication does not help, 
        consult a doctor rather than increasing doses.""",
        "category": "pain"
    },
    {
        "id": "hygiene_basics",
        "content": """Change sanitary pads every 4-6 hours during normal flow, 
        more frequently during heavy flow. Leaving a pad on for more than 8 hours 
        increases infection risk. Wash hands before and after changing pads. 
        Used pads should be wrapped and disposed of properly — never flush pads. 
        Reusable cloth pads are acceptable if washed thoroughly with soap and 
        dried completely in sunlight. Incomplete drying of cloth pads can cause 
        fungal infections.""",
        "category": "hygiene"
    },
    {
        "id": "stigma_and_normalcy",
        "content": """Menstruation is a completely normal, healthy biological process. 
        It is not impure, dirty, or a sign of illness. There is no medical basis for 
        restricting activities during periods — girls can attend school, exercise, 
        cook food, and participate in all normal activities during their period. 
        Period blood is not toxic or harmful to others. Isolating or restricting 
        women during menstruation has no medical justification and causes harm by 
        preventing access to education and normal life.""",
        "category": "education"
    },
]

def build_knowledge_base():
    client = chromadb.PersistentClient(path="./knowledge_db")
    
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    collection = client.get_or_create_collection(
        name="medical_knowledge",
        embedding_function=embedding_fn,
    )
    
    existing = collection.get()
    existing_ids = set(existing["ids"])
    
    new_chunks = [c for c in MEDICAL_KNOWLEDGE if c["id"] not in existing_ids]
    
    if not new_chunks:
        print(f"Knowledge base already has {len(existing_ids)} chunks. Nothing to add.")
        return
    
    collection.add(
        ids=[c["id"] for c in new_chunks],
        documents=[c["content"] for c in new_chunks],
        metadatas=[{"category": c["category"]} for c in new_chunks],
    )
    
    print(f"Added {len(new_chunks)} knowledge chunks to ChromaDB.")
    print(f"Total chunks in knowledge base: {collection.count()}")
    print("\nCategories stored:")
    categories = set(c["category"] for c in MEDICAL_KNOWLEDGE)
    for cat in sorted(categories):
        print(f"  - {cat}")

if __name__ == "__main__":
    build_knowledge_base()

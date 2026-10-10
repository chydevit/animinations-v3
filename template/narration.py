"""Narration and guide dialogue: L(key, Khmer, English) for the narrator, T(key, ...) for the guide.
Write numbers with Khmer digits; khnum.speak() turns them into words for the voice.
Every statement must come from docs/fact_sheet.md.  Label legend, record and debate in the line itself.

SAMPLE CONTENT (Sambor Prei Kuk) — replace it with your film.  Khmer needs native-speaker review."""

N = {}
WHO = {}

# Speakers.  Each one gets ONE locked reference voice: audio/voices/<who>.wav (make.py voices → make.py lock).
VOICES = {
    "nar": dict(label_en="", label_km="",
                design="A warm, calm Cambodian man in his forties, documentary narrator, clear deep voice, measured "
                       "unhurried pace",
                sample="នៅសតវត្សរ៍ទីប្រាំពីរ ទឹកដីកម្ពុជា មានរាជធានីដ៏ធំមួយ ដែលសង់ពីឥដ្ឋ នៅកណ្ដាលព្រៃ។"),
    "tonle": dict(label_en="NEANG TONLE: ", label_km="នាងទន្លេ៖ ",
                  design="A bright, curious Cambodian girl about twelve years old, clear lively youthful voice, friendly",
                  sample="សួស្តី! ខ្ញុំឈ្មោះ នាងទន្លេ។ តើអ្នកចង់ដឹងទេ ថាពីដើមកន្លែងនេះ មានអ្វីខ្លះ?"),
}
GUIDE = "tonle"


def L(key, km, en, who="nar"):
    N[key] = (km, en)
    WHO[key] = who
    return key


def T(key, km, en):
    return L(key, km, en, GUIDE)


# ---------------------------------------------------------------- OPENING
T("t0", "សួស្តី! ខ្ញុំឈ្មោះ នាងទន្លេ។ ខ្ញុំជាតួអង្គប្រឌិត។ ថ្ងៃនេះ យើងទៅលេង សំបូរព្រៃគុក!",
  "Hello! I'm Neang Tonle, a made-up guide. Today we are visiting Sambor Prei Kuk!")

# ---------------------------------------------------------------- 1 THE CITY OF ISANAPURA  [fact sheet §1]
L("a1", "សំបូរព្រៃគុក ស្ថិតនៅក្នុងខេត្តកំពង់ធំ ប្រទេសកម្ពុជា។",
  "Sambor Prei Kuk lies in Kampong Thom province, Cambodia.")
L("a2", "អ្នកប្រវត្តិវិទូ យល់ថា ទីនេះ គឺជាទីក្រុង ឦសានបុរៈ ដែលជារាជធានីរបស់ព្រះបាទ ឦសានវរ្ម័នទី ១ នៅសតវត្សរ៍ទី ៧។",
  "Historians identify it as Isanapura, the capital of King Isanavarman I in the 7th century.")
L("a3", "ប្រាសាទនៅទីនេះ ភាគច្រើនសង់ពីឥដ្ឋ ហើយខ្លះមានរាងប្រាំបីជ្រុង ដែលកម្រឃើញណាស់។",
  "Most of its temples are built of brick, and some are octagonal, which is very rare.")
L("a4", "នៅឆ្នាំ ២០១៧ អង្គការយូណេស្កូ បានចុះបញ្ជី សំបូរព្រៃគុក ជាសម្បត្តិបេតិកភណ្ឌពិភពលោក។",
  "In 2017, UNESCO inscribed Sambor Prei Kuk on the World Heritage List.")
T("t1", "ប្រាសាទទាំងនេះ ចាស់ជាងអង្គរវត្ត ប្រហែលប្រាំរយឆ្នាំ!",
  "These temples are about five hundred years older than Angkor Wat!")

"""Narration and guide dialogue: L(key, Khmer, English, who).  who = "nar" (narrator) or "tonle" (Neang Tonle,
the fictional guide).  Numbers use Khmer digits; khnum.speak() turns them into words for the voice.
Every statement follows docs/fact_sheet.md; legend, record and debate are labelled in the line itself."""

N = {}
WHO = {}
VOICES = {
    "nar": dict(label_en="", label_km="",
                design="A warm, calm Cambodian man in his forties, documentary narrator, clear deep voice, measured "
                       "unhurried pace",
                sample="នៅសតវត្សរ៍ទីមួយនៃគ្រិស្តសករាជ ទឹកដីដីសណ្ដទន្លេមេគង្គ បានក្លាយជាផ្លូវពាណិជ្ជកម្មដ៏សំខាន់មួយ ដែលភ្ជាប់ឥណ្ឌា និងចិន។"),
    "tonle": dict(label_en="NEANG TONLE: ", label_km="នាងទន្លេ៖ ",
                  design="A bright, curious Cambodian girl about twelve years old, clear lively youthful voice, friendly",
                  sample="សួស្តី! ខ្ញុំឈ្មោះ នាងទន្លេ។ ខ្ញុំរស់នៅកំពង់ផែអូរកែវ។ តើអ្នកចង់ដឹងទេ ថាពីដើមកន្លែងនេះ មានអ្វីខ្លះ?"),
}


def L(key, km, en, who="nar"):
    N[key] = (km, en)
    WHO[key] = who
    return key


def T(key, km, en):
    return L(key, km, en, "tonle")


# ---------------------------------------------------------------- 0 OPENING
T("t0", "សួស្តី! ខ្ញុំឈ្មោះ នាងទន្លេ។ ខ្ញុំជាតួអង្គប្រឌិត ជាក្មេងស្រីលក់ដូរតាមទូក មកពីកំពង់ផែអូរកែវ។ ហើយខ្ញុំចូលចិត្តសួរសំណួរណាស់!",
  "Hello! I'm Neang Tonle. I'm a made-up guide: a river-trader girl from the port of Oc Eo. And I love asking questions!")
L("o1", "ពេលព្រលឹម អ័ព្ទរសាត់លើដីសណ្ដទន្លេមេគង្គ។ ប្រហែលពីរពាន់ឆ្នាំមុន ទឹកដីនេះ ស្ថិតនៅចំណុចប្រសព្វ នៃផ្លូវសមុទ្ររវាងឥណ្ឌា និងចិន។",
  "At dawn, mist drifts over the Mekong Delta. Some two thousand years ago, this land stood where the sea routes between India and China met.")
L("o2", "ឯកសារចិនបុរាណ ហៅនគរមួយនៅទីនេះថា ហ្វូណន។ អ្នកប្រាជ្ញជាច្រើន ភ្ជាប់ឈ្មោះនេះ ទៅនឹងពាក្យខ្មែរបុរាណ វ្នំ ដែលមានន័យថា ភ្នំ។ ហេតុនេះហើយ យើងហៅវាថា នគរភ្នំ។ ប៉ុន្តែ អ្នកប្រវត្តិវិទូ នៅតែជជែកគ្នា អំពីន័យនេះ។",
  "Ancient Chinese records called a kingdom here Funan. Many scholars link the name to the Old Khmer word 'vnam', mountain, which is why Cambodians call it Nokor Phnom, the Kingdom of the Mountain. But historians still debate that meaning.")
L("o3", "ក្នុងខ្សែភាពយន្តនេះ យើងនឹងប្រាប់ឲ្យច្បាស់ ថាអ្វីជារឿងព្រេង អ្វីត្រូវបានកត់ត្រា និងអ្វីដែលអ្នកប្រវត្តិវិទូ មិនទាន់ឯកភាពគ្នា។",
  "In this film we will say clearly what is legend, what is recorded, and where historians disagree.")

# ---------------------------------------------------------------- 1 THE LAND BEFORE FUNAN  [fact sheet §3]
T("q1", "តើមុនពេលមានហ្វូណន នៅទីនេះមានអ្វីខ្លះ?", "What was here before Funan?")
L("a1", "មនុស្សបានរស់នៅទីនេះ យូរណាស់មកហើយ មុនពេលមានឈ្មោះហ្វូណន។ នៅអង្គរបុរី ខេត្តតាកែវ អ្នកបុរាណវិទូ បានរកឃើញដានលំនៅដ្ឋាន តាំងពីប្រហែល ៤០០ ឆ្នាំមុនគ្រិស្តសករាជ។",
  "People lived here long before the name Funan. At Angkor Borei, in Takeo, archaeologists have found traces of settlement from around 400 BCE.")
L("a2", "ពួកគេដាំស្រូវ ធ្វើភាជន៍ដី ប្រើលោហៈ ហើយបញ្ចុះសព ជាមួយក្អម អង្កាំ និងសត្វសម្រាប់ថ្វាយ។",
  "They grew rice, made pottery, worked metal, and buried their dead with pots, beads and animal offerings.")
L("a3", "រៀងរាល់ឆ្នាំ ទឹកជំនន់ទន្លេមេគង្គ គ្របដណ្ដប់វាលទំនាប។ វានាំមកនូវដីល្បាប់ និងត្រី ប៉ុន្តែក៏តម្រូវឲ្យមនុស្ស សង់ផ្ទះខ្ពស់ និងរៀនរស់នៅជាមួយទឹក។",
  "Every year the Mekong flood spread across the plains. It brought fertile silt and fish, but it also meant raised houses and a life lived with water.")
L("a4", "សហគមន៍ទាំងនេះ ដោះដូរទំនិញ ឆ្លងកាត់ឈូងសមុទ្រថៃ។ បន្តិចម្ដងៗ ក្នុងរយៈពេលរាប់រយឆ្នាំ ពួកគេបានរីកធំ ហើយកាន់តែស្មុគស្មាញ។",
  "These communities traded across the Gulf of Thailand. Slowly, over several centuries, they grew larger and more complex.")

# ---------------------------------------------------------------- 2 THE FOUNDING LEGEND  [§4]
T("q2", "លោកយាយខ្ញុំ និយាយថា នគរនេះ កើតឡើងពីក្សត្រីយ៍ម្នាក់ និងបុរសម្នាក់ មកពីសមុទ្រ។ តើពិតទេ?",
  "My grandmother says this kingdom began with a queen and a man from the sea. Is that true?")
L("g1", "នោះជារឿងព្រេង មិនមែនជាប្រវត្តិសាស្ត្រដែលបានបញ្ជាក់ទេ។ ហើយវាមានច្រើនកំណែ ពីច្រើនសម័យ។",
  "That is a legend, not proven history, and it comes in several versions from different times.")
L("g2", "កំណែចាស់ជាងគេ គឺកំណែចិន ដែលទូតចិនបានឮ នៅសតវត្សរ៍ទី ៣។ ក្សត្រីយ៍ម្នាក់ ឈ្មោះ លីវយី គ្រប់គ្រងទឹកដីនេះ។",
  "The oldest is the Chinese version, heard by Chinese envoys in the 3rd century. A queen named Liu Ye ruled this land.")
L("g3", "បុរសម្នាក់មកពីប្រទេសឆ្ងាយ ឈ្មោះ ហ៊ុនទៀន សុបិនឃើញអាទិទេពមួយ ប្រគល់ធ្នូដ៏ពិសិដ្ឋឲ្យគាត់។ គាត់ជិះសំពៅពាណិជ្ជករ ឆ្លងសមុទ្រ មកដល់ទីនេះ។",
  "A man from a distant land, Hun Tian, dreamed that a god gave him a sacred bow. He sailed with merchants across the sea and arrived here.")
L("g4", "ពេលលីវយី ចង់វាយយកសំពៅ ហ៊ុនទៀន បាញ់ព្រួញមួយ ទម្លុះចំហៀងទូករបស់នាង។ នាងភ័យខ្លាច ក៏ចុះចាញ់ ហើយរៀបការជាមួយគាត់។",
  "When Liu Ye tried to seize the ship, Hun Tian shot an arrow that pierced the side of her boat. Afraid, she surrendered and married him.")
L("g5", "ឯកសារចិន មិនបានហៅគាត់ថា កៅណ្ឌិន្យ ទេ។ ឈ្មោះ កៅណ្ឌិន្យ និងនាងនាគ សោមា មកពីសិលាចារឹកចាម នៅឆ្នាំ ៦៥៨ និងពីសិលាចារឹកអង្គរ នៅសម័យក្រោយ។",
  "The Chinese records do not call him Kaundinya. The names Kaundinya and the naga princess Soma come from a Cham inscription of 658, and from later Angkorian inscriptions.")
L("g6", "ក្រោយមកទៀត រឿងព្រេងខ្មែរ ព្រះថោង និងនាងនាគ ប្រាប់ពីព្រះអង្គម្ចាស់ ដែលរៀបការជាមួយបុត្រីស្ដេចនាគ។ ស្ដេចនាគ បឺតទឹកសមុទ្រ បង្កើតជាដីគោក។",
  "Later still, the Khmer legend of Preah Thong and Neang Neak tells of a prince who married the daughter of the naga king, who drank up the sea to make dry land.")
L("g7", "សព្វថ្ងៃ កូនកំលោះ នៅតែកាន់ស្បៃកូនក្រមុំ ក្នុងពិធីមង្គលការ ដើម្បីរំលឹករឿងនេះ។ អ្នកប្រវត្តិវិទូខ្លះ យល់ថា រឿងព្រះថោង កើតឡើងយឺតជាងសម័យហ្វូណនច្រើន។",
  "To this day, a Khmer groom holds the bride's sash at the wedding in memory of this story. Some historians think the Preah Thong tale is much later than Funan.")
L("g8", "ដូច្នេះ យើងមានរឿងបី ពីបីសម័យ។ ពួកវាប្រាប់យើង ពីអ្វីដែលមនុស្សជឿ មិនមែនពីអ្វីដែលបានកើតឡើងពិតនោះទេ។",
  "So these are three stories from three eras. They tell us what people believed, not exactly what happened.")

# ---------------------------------------------------------------- 3 OC EO, PORT OF THE WORLD  [§7]
T("q3", "កំពង់ផែរបស់ខ្ញុំ មានសំពៅមកពីគ្រប់ទិសទី! តើពួកគេមកពីណាខ្លះ?",
  "Ships come to my port from everywhere! Where do they all come from?")
L("p1", "អូរកែវ ស្ថិតនៅជើងភ្នំបាថេ ក្នុងខេត្តអានយ៉ាង ភាគខាងត្បូងប្រទេសវៀតណាមសព្វថ្ងៃ។ វារីកចម្រើនខ្លាំង ចាប់ពីប្រហែលសតវត្សរ៍ទី ២ ដល់ទី ៦។",
  "Oc Eo lies at the foot of Ba The mountain, in An Giang, in today's southern Vietnam. It flourished from about the 2nd to the 6th century.")
L("p2", "នៅឆ្នាំ ១៩៤៤ អ្នកបុរាណវិទូបារាំង លោក លូអ៊ី ម៉ាឡឺរ៉េ បានធ្វើកំណាយនៅទីនោះ ហើយបានរកឃើញទីក្រុងមួយ ធំប្រហែល ៤៥០ ហិកតា ដែលមានប្រឡាយកាត់កណ្ដាល។",
  "In 1944, the French archaeologist Louis Malleret excavated there and revealed a city of about 450 hectares, crossed by canals.")
L("p3", "ជាងមាសនៅទីនោះ ធ្វើចិញ្ចៀន ក្រវិល និងស្លឹកមាស។ ជាងអង្កាំ ធ្វើអង្កាំកែវ និងអង្កាំថ្ម រាប់មិនអស់។",
  "Goldsmiths made rings, earrings and gold foil. Bead-makers produced glass and stone beads beyond counting.")
L("p4", "គេក៏រកឃើញត្រាតូចៗ ធ្វើពីថ្មត្បូង ដែលឆ្លាក់ឈ្មោះមនុស្ស ជាអក្សរឥណ្ឌាបុរាណ។",
  "Small seals cut in gemstones carry personal names in an ancient Indian script.")
L("p5", "ទំនិញ និងគំនិត បានមកដល់ពីឥណ្ឌា ពីចិន ហើយសូម្បីតែពីពិភពរ៉ូម៉ាំងឆ្ងាយ តាមរយៈពាណិជ្ជករជាច្រើនដៃ។ គេរកឃើញកញ្ចក់សំរិទ្ធចិន សម័យហាន និងភាជន៍ឥណ្ឌា។",
  "Goods and ideas arrived from India, from China, and even from the distant Roman world, passed along by many hands. Han Chinese bronze mirrors and Indian pottery have been found.")
L("p6", "របស់ល្បីបំផុតមួយ គឺដុំមាស ដែលមានរូបព្រះចៅអធិរាជរ៉ូម៉ាំង អង់តូនីនុស ពីយុស ពីពាក់កណ្ដាលសតវត្សរ៍ទី ២។ អ្នកស្រាវជ្រាវជាច្រើន យល់ថា វាជាគ្រឿងអលង្ការ ដែលធ្វើតាមកាក់រ៉ូម៉ាំង។",
  "One of the most famous finds is a gold piece bearing the image of the Roman emperor Antoninus Pius, from the mid-2nd century. Many researchers think it is jewellery made to imitate a Roman coin.")
L("p7", "វាមិនបង្ហាញថា ជនជាតិរ៉ូម៉ាំង បានមកដល់អូរកែវទេ។ វាបង្ហាញថា អូរកែវ ស្ថិតនៅលើបណ្ដាញពាណិជ្ជកម្ម ដែលលាតសន្ធឹងពាក់កណ្ដាលពិភពលោក។",
  "It does not show that Romans came to Oc Eo. It shows that Oc Eo sat on a trading network stretching halfway across the world.")
L("p8", "នៅឆ្នាំ ២០២៣ អ្នកវិទ្យាសាស្ត្រ បានរកឃើញដានគ្រឿងទេស ដូចជា រមៀត ខ្ញី និងគ្រឿងទេសផ្សេងទៀត លើថ្មកិនរបស់អូរកែវ។",
  "In 2023, scientists found traces of spices, such as turmeric and ginger, on Oc Eo's grinding stones.")

# ---------------------------------------------------------------- 4 MASTERS OF WATER  [§8]
T("q4", "ខ្ញុំអុំទូកតាមប្រឡាយ រហូតដល់អង្គរបុរី។ តើនរណាជាអ្នកជីកប្រឡាយទាំងនេះ?",
  "I paddle along the canal all the way to Angkor Borei. Who dug these canals?")
L("w1", "នៅទសវត្សរ៍ ១៩៣០ រូបថតពីលើអាកាស បានបង្ហាញខ្សែត្រង់ៗ វែងៗ កាត់វាលទំនាប។ ពួកវាជាប្រឡាយបុរាណ។",
  "In the 1930s, aerial photographs revealed long, straight lines across the plain. They were ancient canals.")
L("w2", "ប្រឡាយមួយ ភ្ជាប់អូរកែវ ទៅអង្គរបុរី មានប្រវែងប្រហែល ៧០ គីឡូម៉ែត្រ។ ប្រឡាយផ្សេងទៀត រត់ឆ្ពោះទៅឆ្នេរសមុទ្រ។",
  "One links Oc Eo to Angkor Borei, about 70 kilometres long. Others ran towards the coast.")
L("w3", "អង្គរបុរី មានកំពែងឥដ្ឋ និងគូទឹក ព័ទ្ធជុំវិញផ្ទៃដីយ៉ាងតិច ៣០០ ហិកតា ហើយមានសំណង់ឥដ្ឋ ជាងដប់កន្លែង។",
  "Angkor Borei had brick walls and moats enclosing at least 300 hectares, and more than a dozen brick monuments.")
L("w4", "ការសិក្សាលើប្រឡាយមួយ ក្បែរអង្គរបុរី បង្ហាញថា វាត្រូវបានជីក មុនពាក់កណ្ដាលសហស្សវត្សរ៍ទីមួយនៃគ្រិស្តសករាជ ហើយចាប់ផ្ដើមកកដីល្បាប់ ប្រហែលសតវត្សរ៍ទី ៤ ឬទី ៥។",
  "A study of one canal near Angkor Borei shows it was dug before the middle of the first millennium CE, and began to silt up around the 4th or 5th century.")
L("w5", "ប្រឡាយទាំងនេះ ប្រហែលជាសម្រាប់ដឹកជញ្ជូន និងបង្ហូរទឹក ហើយប្រហែលជាសម្រាប់ស្រោចស្រពផងដែរ។ ការជីកវា ទាមទារកម្លាំងពលកម្ម និងការរៀបចំយ៉ាងច្រើន។",
  "They were probably used for transport and drainage, perhaps for irrigation too. Digging them took a great deal of organised labour.")

# ---------------------------------------------------------------- 5 FAN SHIMAN  [§5, §9]
T("q5", "ខ្ញុំឮថា ស្ដេចមួយអង្គ មាននាវាធំៗជាច្រើន។ តើព្រះអង្គទៅដល់ណា?",
  "I heard one king had many great ships. How far did he go?")
L("f1", "នៅដើមសតវត្សរ៍ទី ៣ យោងតាមឯកសារចិន មេដឹកនាំម្នាក់ ឈ្មោះ ហ្វានស៊ីម៉ាន បានឡើងកាន់អំណាច។ គាត់ហៅខ្លួនឯងថា មហាក្សត្រហ្វូណន។",
  "In the early 3rd century, according to Chinese records, a leader named Fan Shiman came to power. He called himself 'Great King of Funan'.")
L("f2", "គាត់បានសង់នាវាធំៗ ឆ្លងសមុទ្រ ហើយវាយលុកនគរជាងដប់ ប្រហែលជាតាមឆ្នេរ រហូតដល់ឧបទ្វីបម៉ាឡេ។",
  "He built great ships, crossed the sea and attacked more than ten states, perhaps along the coasts as far as the Malay Peninsula.")
L("f3", "ឯកសារចិន ពិពណ៌នាថា ទូករបស់ហ្វូណន វែងប្រហែល ២០ ម៉ែត្រ តូចចង្អៀត ហើយមានក្បាល និងកន្ទុយ ដូចត្រី។",
  "Chinese texts describe Funan's boats as about 20 metres long and narrow, with bow and stern shaped like a fish.")
L("f4", "គាត់ធ្លាក់ខ្លួនឈឺ ពេលរៀបចំវាយនគរមួយទៀត ឈ្មោះ ជីនលីន។",
  "He fell ill while preparing to attack yet another state, Jinlin.")
L("f5", "ប៉ុន្តែ ព័ត៌មានទាំងនេះ ភាគច្រើនមកពីឯកសារចិន ដែលសរសេររាប់រយឆ្នាំក្រោយមក។ យើងមិនអាចដឹងច្បាស់ ថាអំណាចរបស់គាត់ លាតសន្ធឹងដល់ណាទេ។ ទំនិញដូចគ្នា មិនមែនមានន័យថា មានការគ្រប់គ្រងនយោបាយជានិច្ចនោះទេ។",
  "But most of this comes from Chinese texts written centuries later. We cannot know exactly how far his power reached, and shared trade goods do not always mean political control.")

# ---------------------------------------------------------------- 6 ENVOYS FROM CHINA  [§6]
T("q6", "មានភ្ញៀវចិនពីរនាក់ មកដល់វាំង! តើពួកគេសរសេរអ្វីខ្លះ អំពីយើង?",
  "Two Chinese visitors have come to the palace! What did they write about us?")
L("c1", "នៅពាក់កណ្ដាលសតវត្សរ៍ទី ៣ នគរអ៊ូ របស់ចិន បានបញ្ជូនទូតពីរនាក់ គឺ ខាងថាយ និង ជូយិង មកកាន់ហ្វូណន ក្នុងរជ្ជកាល ហ្វានស៊ុន។",
  "In the mid-3rd century, the Chinese kingdom of Wu sent two envoys, Kang Tai and Zhu Ying, to Funan, in the reign of Fan Xun.")
L("c2", "សៀវភៅរបស់ពួកគេ បានបាត់បង់ ប៉ុន្តែប្រវត្តិសាស្ត្ររាជវង្សចិន សម័យក្រោយ បានដកស្រង់ពីវា។",
  "Their books are lost, but later Chinese dynastic histories quoted from them.")
L("c3", "ពួកគេបានឃើញទីក្រុងមានកំពែង វាំង និងផ្ទះខ្ពស់ៗ។ មនុស្សនៅទីនោះ ធ្វើស្រែចម្ការ ចូលចិត្តការឆ្លាក់ និងប្រើចានធ្វើពីប្រាក់។",
  "They saw walled towns, palaces and raised houses. People farmed, loved carving, and ate from vessels of silver.")
L("c4", "ពន្ធ ត្រូវបានបង់ជា មាស ប្រាក់ គុជ និងគ្រឿងក្រអូប។ ពួកគេក៏មានសៀវភៅ និងបណ្ណសារ ដែលអក្សរ ស្រដៀងនឹងអក្សររបស់ប្រជាជនខាងលិច ប្រហែលជាអក្សរឥណ្ឌា។",
  "Taxes were paid in gold, silver, pearls and perfumes. They also kept books and archives, in a script like that of the peoples to the west, probably an Indian script.")
L("c5", "ឯកសារចិន ក៏រៀបរាប់ពីរូបរាងមនុស្ស ដោយការរើសអើងនៃសម័យនោះ។ ការពិពណ៌នាបែបនេះ ប្រាប់យើងច្រើនអំពីអ្នកសង្កេត ជាងអំពីប្រជាជនហ្វូណន។",
  "Chinese writers also described people's looks with the prejudices of their time. Such descriptions tell us more about the observers than about the people of Funan.")
L("c6", "ទោះជាយ៉ាងណា ឯកសារចិន នៅតែជាប្រភពសរសេរដ៏សំខាន់បំផុត អំពីហ្វូណន ព្រោះគ្មានឯកសារហ្វូណនណាមួយ ប្រាប់ពីប្រវត្តិរបស់ខ្លួនទេ។",
  "Even so, Chinese records remain our most important written source on Funan, because no Funan text tells its own history.")

# ---------------------------------------------------------------- 7 FAITH AND IDEAS FROM INDIA  [§10]
T("q7", "លោកព្រាហ្មណ៍ និងព្រះសង្ឃ មកដល់តាមសំពៅ។ ហេតុអ្វីបានជាពួកលោក មកទីនេះ?",
  "Brahmins and monks arrive by ship. Why do they come here?")
L("i1", "តាមផ្លូវពាណិជ្ជកម្ម មិនមែនមានតែទំនិញទេ ដែលមកដល់។ ភាសាសំស្ក្រឹត ព្រហ្មញ្ញសាសនា ព្រះពុទ្ធសាសនា និងគំនិតអំពីរាជ្យ ក៏បានមកដល់ពីឥណ្ឌាដែរ។",
  "Along the trade routes came more than goods. Sanskrit, Hinduism, Buddhism and ideas of kingship also arrived from India.")
L("i2", "ឯកសារចិនប្រាប់ថា នៅប្រហែលចុងសតវត្សរ៍ទី ៤ ឬដើមសតវត្សរ៍ទី ៥ ស្ដេចម្នាក់ ដែលចិនហៅថា កៅណ្ឌិន្យ ជាព្រាហ្មណ៍មកពីឥណ្ឌា បានកែប្រែច្បាប់ តាមរបៀបឥណ្ឌា។",
  "Chinese records say that around the late 4th or early 5th century, a king they called Kaundinya, 'a brahmin from India', changed the laws to follow Indian ways.")
L("i3", "អ្នកប្រវត្តិវិទូខ្លះ គិតថា គាត់ពិតជាមកពីឥណ្ឌាមែន។ អ្នកខ្លះទៀត យល់ថា ស្ដេចក្នុងស្រុក បានយកឈ្មោះ និងរឿងព្រេង កៅណ្ឌិន្យ មកប្រើ។",
  "Some historians think he really came from India. Others think local kings adopted the Kaundinya name and legend.")
L("i4", "ចាប់ពីសតវត្សរ៍ទី ៥ មក ឈ្មោះស្ដេច ចាប់ផ្ដើមបញ្ចប់ដោយពាក្យ វរ្ម័ន ដែលជាពាក្យសំស្ក្រឹត មានន័យថា អាវក្រោះ ឬអ្នកការពារ។",
  "From the 5th century, kings' names began to end in '-varman', a Sanskrit word meaning 'armour' or 'protector'.")
L("i5", "សិលាចារឹកសំស្ក្រឹតមួយ ពីសតវត្សរ៍ទី ៥ ដែលរកឃើញនៅហ្គោថាប ប្រាប់ពីព្រះអង្គម្ចាស់ គុណវរ្ម័ន ក្នុងវង្សកៅណ្ឌិន្យ ដែលបានតម្កល់ស្នាមព្រះបាទ របស់ព្រះវិស្ណុ។",
  "A 5th-century Sanskrit inscription found at Go Thap tells of Prince Gunavarman, of the lineage of Kaundinya, who installed a footprint of Vishnu.")
L("i6", "ប្រជាជនហ្វូណន បានជ្រើសរើស និងកែសម្រួលគំនិតទាំងនេះ តាមជីវិតរបស់ខ្លួន។ ពួកគេមិនមែនគ្រាន់តែជាអាណានិគមនោះទេ។ ទ្រឹស្តីអាណានិគមឥណ្ឌា ជាគំនិតចាស់មួយ ដែលអ្នកប្រវត្តិវិទូជាច្រើន សព្វថ្ងៃ មិនយល់ស្របទេ។",
  "Funan's people chose and adapted these ideas; they were not simply colonised. The old theory of Indian colonies is one that many historians now question.")

# ---------------------------------------------------------------- 8 LIFE, ART AND SOCIETY  [§11]
T("q8", "តើមនុស្សនៅសម័យខ្ញុំ រស់នៅយ៉ាងដូចម្ដេច?", "How did people live in my time?")
L("l1", "យោងតាមឯកសារចិន បុរសស្លៀកក្រណាត់រុំ ហៅថា កានម៉ាន់។ អ្នកមានប្រើក្រណាត់ប៉ាក់ អ្នកក្រប្រើក្រណាត់ធម្មតា។ ស្ត្រីពាក់ក្រណាត់មួយ ដែលមានរន្ធដាក់ក្បាល។",
  "According to Chinese records, men wore a wrapped cloth called 'ganman': brocade for the rich, plain cloth for the poor. Women wore a cloth with an opening for the head.")
L("l2", "ជាងធ្វើចិញ្ចៀនមាស កងដៃ និងចានប្រាក់។ មនុស្សចូលចិត្តការប្រកួតមាន់ និងជ្រូក។ ស្ដេចជិះដំរី ហើយស្ត្រីក៏អាចជិះដំរីបានដែរ។",
  "Smiths made gold rings, bracelets and silver dishes. People enjoyed cockfights and pig fights. The king rode an elephant, and women could ride elephants too.")
L("l3", "គ្មានគុកទេ។ ការកាត់ក្ដី ធ្វើឡើងតាមការសាកល្បង ដូចជាការលូកយកចិញ្ចៀនមាស ពីក្នុងទឹកពុះ។ គេជឿថា មនុស្សស្លូតត្រង់ នឹងមិនរងរបួសទេ។",
  "There were no prisons. Justice was by ordeal, such as pulling a gold ring out of boiling water; the innocent, it was believed, would not be harmed.")
L("l4", "នៅឆ្នាំ ២៤៣ ស្ដេចហ្វូណន បានបញ្ជូនតន្ត្រីករ ទៅរាជវាំងចិន។ យើងមិនដឹងថា ពួកគេលេងឧបករណ៍ភ្លេងអ្វីខ្លះទេ។",
  "In 243, a Funan king sent musicians to the Chinese court. We do not know what instruments they played.")
L("l5", "សិល្បៈថ្មដ៏ល្បីបំផុត មកពីភ្នំដា ក្បែរអង្គរបុរី៖ រូបចម្លាក់ព្រះវិស្ណុ ព្រះក្រឹស្ណ និងព្រះពលរាម ដែលសព្វថ្ងៃ តាំងនៅសារមន្ទីរជាតិ ភ្នំពេញ។",
  "The most famous stone art comes from Phnom Da near Angkor Borei: statues of Vishnu, Krishna and Balarama, now in the National Museum in Phnom Penh.")
L("l6", "ប៉ុន្តែ អ្នកប្រវត្តិវិទូ មិនទាន់ឯកភាពថា ពួកវាធ្វើនៅចុងសម័យហ្វូណន ក្នុងសតវត្សរ៍ទី ៦ ឬនៅដើមសម័យចេនឡា ក្នុងសតវត្សរ៍ទី ៧ នោះទេ។",
  "But historians disagree whether they were made at the end of Funan, in the 6th century, or in early Chenla times, in the 7th.")

# ---------------------------------------------------------------- 9 THE LAST GREAT KINGS  [§12]
T("q9", "តើស្ដេចហ្វូណនចុងក្រោយ ជានរណា?", "Who were the last kings of Funan?")
L("k1", "នៅឆ្នាំ ៤៨៤ ស្ដេចជ័យវរ្ម័ន បានបញ្ជូនព្រះសង្ឃឥណ្ឌាមួយរូប ឈ្មោះ នាគសេន ទៅកាន់រាជវាំងចិន ជាមួយលិខិត និងអំណោយ។",
  "In 484, King Jayavarman sent an Indian monk, Nagasena, to the Chinese court with a letter and gifts.")
L("k2", "លិខិតនោះ សរសើរព្រះឥសូរ ដែលចុះមកលើភ្នំមួយ ហើយក៏សរសើរព្រះពុទ្ធផងដែរ។ អំណោយ មានរូបស្ដេចនាគ ដែលលម្អដោយមាស និងចេតិយភ្លុកដំរីពីរ។",
  "The letter praised Shiva descending on a mountain, and also praised the Buddha. The gifts included a gold-worked image of a naga king and two ivory stupas.")
L("k3", "ក្រោយមក ចិនបានផ្ដល់ងារដល់ជ័យវរ្ម័ន ថា ស្ដេចហ្វូណន។ ព្រះអង្គសោយទិវង្គត នៅឆ្នាំ ៥១៤។",
  "Later, China granted Jayavarman the title 'King of Funan'. He died in 514.")
L("k4", "ព្រះសង្ឃហ្វូណនពីររូប គឺ សង្ឃបាល និង មន្ទ្រសេន បានធ្វើដំណើរទៅទីក្រុងណានជីង ហើយបកប្រែគម្ពីរព្រះពុទ្ធសាសនា ជាភាសាចិន។",
  "Two Funan monks, Sanghapala and Mandrasena, travelled to Nanjing and translated Buddhist scriptures into Chinese.")
L("k5", "សង្ឃបាល បានបកប្រែ ពីឆ្នាំ ៥០៦ ដល់ឆ្នាំ ៥១៨ ហើយព្រះចៅអធិរាជចិនផ្ទាល់ បានចូលរួមក្នុងវគ្គដំបូង។",
  "Sanghapala translated from 506 to 518, and the Chinese emperor himself attended the first session.")
L("k6", "បន្ទាប់ពីជ័យវរ្ម័ន បុត្ររបស់ព្រះអង្គ រុទ្រវរ្ម័ន បានឡើងគ្រងរាជ្យ។ សិលាចារឹកមួយ នៅតាព្រហ្មបាទី បញ្ជាក់ថា រុទ្រវរ្ម័ន ជាបុត្ររបស់ជ័យវរ្ម័ន ដូចឯកសារចិនដែរ។",
  "After Jayavarman, his son Rudravarman took the throne. An inscription at Ta Prohm of Bati names Rudravarman as Jayavarman's son, just as the Chinese records do.")
L("k7", "នៅឆ្នាំ ៥៣៩ រុទ្រវរ្ម័ន បានបញ្ជូនរមាសរស់មួយ ទៅប្រទេសចិន។ ព្រះអង្គគឺជាស្ដេចហ្វូណនចុងក្រោយ ដែលមានឈ្មោះ ក្នុងឯកសារចិន។",
  "In 539, Rudravarman sent a live rhinoceros to China. He is the last Funan king named in Chinese records.")

# ---------------------------------------------------------------- 10 DECLINE AND THE RISE OF CHENLA  [§13]
T("q10", "ហេតុអ្វីបានជាសំពៅ មកកំពង់ផែយើង តិចជាងមុន?", "Why do fewer ships come to our port now?")
L("d1", "អ្នកប្រវត្តិវិទូ សន្មតថា ចាប់ពីសតវត្សរ៍ទី ៥ និងទី ៦ នាវាកាន់តែច្រើន បើកដោយផ្ទាល់ ឆ្លងកាត់ច្រកសមុទ្រម៉ាឡាកា ទៅប្រទេសចិន ដោយមិនឈប់នៅឆ្នេរហ្វូណន។",
  "Historians suggest that from the 5th and 6th centuries, more ships sailed directly through the Strait of Malacca to China, without stopping on Funan's coast.")
L("d2", "ប្រឡាយខ្លះ ចាប់ផ្ដើមកកដីល្បាប់ ហើយមជ្ឈមណ្ឌលថ្មីៗ បានរីកចម្រើន នៅតំបន់ខាងក្នុងដី ឆ្ពោះទៅខាងជើង។",
  "Some canals were silting up, and new centres were growing inland, to the north.")
L("d3", "ប្រវត្តិសាស្ត្ររាជវង្សស៊ុយ របស់ចិន ប្រាប់ថា ចេនឡា ពីដើមជានគរចំណុះហ្វូណន ហើយស្ដេចចិត្រសេន បានវាយយកហ្វូណន។ ឯកសារក្រោយៗទៀត និយាយថា ជាស្ដេចឦសានវរ្ម័នវិញ។",
  "The Chinese history of the Sui says Chenla was once a vassal of Funan, and that King Chitrasena annexed it. A much later record names King Isanavarman instead.")
L("d4", "សិលាចារឹកបង្ហាញថា ភវវរ្ម័ន និង ចិត្រសេន មានសកម្មភាព នៅចុងសតវត្សរ៍ទី ៦។ ក្រោយមក ឦសានវរ្ម័ន គ្រប់គ្រងពីសំបូរព្រៃគុក។",
  "Inscriptions show Bhavavarman and Chitrasena active in the late 6th century; later, Isanavarman ruled from Sambor Prei Kuk.")
L("d5", "តើនេះជាការវាយដណ្ដើម ឬជាការផ្លាស់ប្ដូរបន្តិចម្ដងៗ? អ្នកប្រវត្តិវិទូ នៅតែជជែកវែកញែក។ សិលាចារឹកមួយ ប្រាប់ពីគ្រួសារមួយ ដែលបម្រើស្ដេចរុទ្រវរ្ម័ន ហើយបន្តបម្រើស្ដេចចេនឡា។",
  "Was it conquest, or gradual change? Historians still debate. One inscription tells of a family that served Rudravarman and went on to serve the kings of Chenla.")

# ---------------------------------------------------------------- CLOSING: LEGACY  [§14]
T("q11", "ដូច្នេះ ហ្វូណន បាត់ទៅហើយឬ?", "So, is Funan gone?")
L("z1", "ហ្វូណន មិនមែនជាចក្រភពអង្គរទេ ហើយប្រហែលជាមិនមែនជានគរតែមួយផង។ យើងក៏មិនដឹងច្បាស់ដែរ ថាប្រជាជនរបស់វា និយាយភាសាអ្វី។",
  "Funan was not the Angkor Empire, and it may not have been a single kingdom at all. We do not even know for certain what language its people spoke.")
L("z2", "ប៉ុន្តែ សិលាចារឹកភាសាខ្មែរ ដែលមានកាលបរិច្ឆេទចាស់ជាងគេ នៅឆ្នាំ ៦១១ មកពីអង្គរបុរី ក្នុងតំបន់ស្នូលនៃហ្វូណនចាស់។ ហើយស្ដេចអង្គរ ក្រោយមក បានអះអាងថា ខ្លួនជាពូជពង្សរបស់ កៅណ្ឌិន្យ និងសោមា។",
  "Yet the oldest dated inscription in Khmer, from 611, comes from Angkor Borei, in the old Funan heartland. And later Angkorian kings claimed descent from Kaundinya and Soma.")
L("z3", "កំពង់ផែ ប្រឡាយ ប្រាសាទ និងប្រពៃណីរាជ្យរបស់ហ្វូណន ស្ថិតក្នុងចំណោមឫសគល់ដ៏ជ្រៅបំផុត នៃអរិយធម៌កម្ពុជា។",
  "Funan's ports, canals, temples and royal traditions are among the deepest roots of Cambodian civilisation.")
T("t12", "ខ្ញុំនឹងបណ្ដែតផ្កាឈូកនេះ តាមទឹកទន្លេ ដើម្បីរំលឹកដល់មនុស្សទាំងអស់ ដែលបានរស់នៅទីនេះ មុនយើង។",
  "I'll float this lotus down the river, to remember everyone who lived here before us.")

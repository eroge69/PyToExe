import streamlit as st
from difflib import SequenceMatcher

# 유사도 계산 함수
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 60문항 데이터 정의
questions = [
    # Short Answer (1–20)
    {"type": "sa", "question": "1. 합성생물학(Synthetic Biology)의 정의를 1~2문장으로 서술하시오.", "answer": "합성생물학은 생물학적 시스템을 공학 원리로 설계·제어하는 학문이다."},
    {"type": "sa", "question": "2. DNA의 이중 나선 구조에서 G-C 쌍이 A-T 쌍보다 더 안정적인 이유는 무엇인가?", "answer": "G-C 쌍은 세 개의 수소 결합을 형성해 A-T 쌍(두 개 수소 결합)보다 안정적이다."},
    {"type": "sa", "question": "3. 반보완적 복제(semi-conservative replication)의 개념을 설명하시오.", "answer": "새로운 이중나선은 하나의 기존 가닥과 하나의 새로 합성된 가닥으로 구성된다."},
    {"type": "sa", "question": "4. PCR의 3단계(변성, 결합, 신장)를 간단히 설명하시오.", "answer": "변성: 94~98℃ 가열 → 결합: 50~65℃에서 프라이머 결합 → 신장: 72℃에서 DNA 중합효소 작용"},
    {"type": "sa", "question": "5. 중심원리(Central Dogma)를 구성하는 3가지 단계와 각 단계에서 일어나는 분자적 변화를 서술하시오.", "answer": "DNA 전사 → RNA 생성, RNA 번역 → 단백질 생성 → 단백질 기능 수행"},
    {"type": "sa", "question": "6. 코돈(Codon)의 개수와 그 중 아미노산을 지정하지 않는 코돈 수는 각각 얼마인가?", "answer": "64개 코돈 중 3개는 종결코돈이고 61개는 아미노산을 지정한다."},
    {"type": "sa", "question": "7. 단백질의 1차, 2차, 3차, 4차 구조를 정의하시오.", "answer": "1차: 아미노산 서열, 2차: α-나선/β-병풍, 3차: 단일 폴리펩티드 입체 구조, 4차: 다중 폴리펩티드 서브유닛 구조"},
    {"type": "sa", "question": "8. 프로모터(promoter)와 오페론(operon)의 차이를 간단히 서술하시오.", "answer": "프로모터는 전사 시작 부위, 오페론은 하나의 프로모터로 조절되는 여러 유전자 군이다."},
    {"type": "sa", "question": "9. RNA 간섭(RNAi)의 주요 단계를 순서대로 나열하시오.", "answer": "dsRNA 절단 → Dicer 처리 → si/miRNA 형성 → RISC 결합 → mRNA 분해 또는 번역 억제"},
    {"type": "sa", "question": "10. siRNA와 miRNA의 작용 방식 차이점을 서술하시오.", "answer": "siRNA는 완전 상보 결합으로 mRNA를 절단하고, miRNA는 부분 상보 결합으로 번역을 억제한다."},
    {"type": "sa", "question": "11. lncRNA가 유전자 발현을 조절하는 방식 중 두 가지를 예시와 함께 설명하시오.", "answer": "XIST: X염색체 불활성화, HOTAIR: 크로마틴 리모델링 매개"},
    {"type": "sa", "question": "12. riboswitch가 리간드에 반응하여 유전자 발현을 억제하는 메커니즘을 설명하시오.", "answer": "리간드 결합 시 RNA 2차 구조가 변형되어 전사 종결 또는 RBS 차단이 일어난다."},
    {"type": "sa", "question": "13. CRISPR-Cas9 시스템에서 가이드 RNA(gRNA)의 역할은 무엇인가?", "answer": "표적 DNA 서열을 인식하도록 Cas9 단백질을 안내한다."},
    {"type": "sa", "question": "14. HDR과 NHEJ 복구 메커니즘의 차이점을 서술하시오.", "answer": "NHEJ는 빠르지만 무작위 삽입/결실이 발생, HDR은 제공된 서열 기반의 정확 복구가 가능하다."},
    {"type": "sa", "question": "15. Parts-Devices-Systems 접근법에서 각각의 계층이 의미하는 바를 설명하시오.", "answer": "Parts: 기본 DNA 요소, Devices: 부품 조합 기능, Systems: 여러 장치의 결합으로 복합 기능 수행."},
    {"type": "sa", "question": "16. 합성생물학의 설계 주기(Design-Build-Test-Learn)의 각 단계를 간단히 설명하시오.", "answer": "설계: 모델링 → 제작: DNA 합성 → 테스트: 기능 검증 → 학습: 데이터 분석 및 최적화 반복."},
    {"type": "sa", "question": "17. Golden Gate Cloning의 핵심 원리와 장점은 무엇인가?", "answer": "Type IIS 제한효소로 절단 후 한 번의 반응으로 다중 DNA 부품을 빠르게 조립할 수 있다."},
    {"type": "sa", "question": "18. BioCAD의 정의와 주요 활용 목적을 기술하시오.", "answer": "합성생물학 CAD는 회로 설계, 시뮬레이션, 자동 DNA 조립 워크플로우를 지원하는 도구이다."},
    {"type": "sa", "question": "19. 생물학적 논리 게이트 AND, OR, NOT의 생물학적 구현 예시를 각각 설명하시오.", "answer": "AND: 두 유도물 모두 필요, OR: 하나만 있으면 발현, NOT: 억제자 존재 시만 발현."},
    {"type": "sa", "question": "20. 유전자 발현의 시간 조절을 위해 사용되는 합성 생물학적 발진기(Oscillator)의 개념을 설명하시오.", "answer": "Repressilator와 같은 피드백 루프 기반의 주기적 전사-번역 발진 시스템이다."},

    # Multiple Choice (21–80)
    {"type":"mc","question":"21. 합성생물학에서 '모듈화(Modularity)'의 의미로 가장 적절한 것은?","options":["실험을 컴퓨터로 대체하는 것","유전자 서열의 자동 번역","생물학적 시스템을 독립적인 부품으로 나누어 설계","RNA만으로 유전자를 조절하는 것"],"correct":2,"explanation":"정답 C: 모듈화는 부품 단위로 설계하는 개념입니다."},
    {"type":"mc","question":"22. DNA 복제에서 새로운 가닥은 어느 방향으로 합성되는가?","options":["3’→5’","5’→3’","양방향","무작위 방향"],"correct":1,"explanation":"정답 B: DNA는 5’→3’ 방향으로 합성됩니다."},
    {"type":"mc","question":"23. RNA 전사 과정에서 A 염기는 RNA에서 어떤 염기와 상보적인가?","options":["A","G","T","U"],"correct":3,"explanation":"정답 D: RNA에서 A는 U와 상보 결합합니다."},
    {"type":"mc","question":"24. PCR의 Annealing 단계에서 일어나는 반응은?","options":["DNA 이중나선 분리","프라이머와 DNA 주형 결합","DNA 복구","RNA 전사"],"correct":1,"explanation":"정답 B: 프라이머가 주형 DNA에 결합합니다."},
    {"type":"mc","question":"25. 다음 중 유전 암호의 특징으로 옳은 것은?","options":["코돈 하나가 두 아미노산 지정","모든 코돈이 번역 종결","중복성(Degeneracy)","모든 유전자가 5개 코돈만 사용"],"correct":2,"explanation":"정답 C: 유전 암호는 중복성을 가집니다."},
    {"type":"mc","question":"26. 다음 중 RNA 중합효소가 결합하는 DNA 서열은?","options":["Operator","Terminator","Promoter","Enhancer"],"correct":2,"explanation":"정답 C: Promoter에 RNA 중합효소가 결합합니다."},
    {"type":"mc","question":"27. siRNA의 특징으로 틀린 것은?","options":["강력한 유전자 억제","mRNA 3’ UTR만 결합","dsRNA 유래","RNAi 핵심 역할"],"correct":1,"explanation":"정답 B: siRNA는 다양한 부위와 결합합니다."},
    {"type":"mc","question":"28. 다음 중 riboswitch의 기능이 아닌 것은?","options":["단백질 없이 조절","리간드 결합 구조 변화","DNA 복제 시작","전사·번역 억제"],"correct":2,"explanation":"정답 C: riboswitch는 DNA 복제를 시작하지 않습니다."},
    {"type":"mc","question":"29. CRISPR-Cas9에서 Cas9 단백질의 주요 기능은?","options":["DNA 중합","RNA 복제","표적 DNA 절단","단백질 접힘"],"correct":2,"explanation":"정답 C: Cas9은 표적 DNA를 절단합니다."},
    {"type":"mc","question":"30. Golden Gate Cloning에서 사용되는 제한효소는?","options":["EcoRI","BsaI","BamHI","HindIII"],"correct":1,"explanation":"정답 B: BsaI입니다."},
    {"type":"mc","question":"31. 합성생물학 설계 주기에서 'Learn' 단계의 역할은?","options":["설계 제거","실험 데이터 기반 개선","모델링 실행","리간드 선택"],"correct":1,"explanation":"정답 B: 실험 데이터를 기반으로 개선합니다."},
    {"type":"mc","question":"32. 다음 중 생물학적 장치(Devices)의 예시로 적절한 것은?","options":["Promoter","Lac Operon","유전자 회로","코돈"],"correct":2,"explanation":"정답 C: 유전자 회로입니다."},
    {"type":"mc","question":"33. Parts-Devices-Systems 계층 구조에서 가장 상위 계층은?","options":["Parts","Devices","Systems","Circuits"],"correct":2,"explanation":"정답 C: Systems입니다."},
    {"type":"mc","question":"34. 다음 중 유전자 회로 설계에 사용되는 소프트웨어가 아닌 것은?","options":["Clotho","GenoCAD","Excel","TinkerCell"],"correct":2,"explanation":"정답 C: Excel은 아닙니다."},
    {"type":"mc","question":"35. 미생물 샤시(Chassis)로 널리 사용되는 생물종이 아닌 것은?","options":["E. coli","S. cerevisiae","Homo sapiens","B. subtilis"],"correct":2,"explanation":"정답 C: Homo sapiens는 아닙니다."},
    {"type":"mc","question":"36. DNA 합성에 사용되지 않는 기술은?","options":["PCR","Restriction Cloning","RNA splicing","Gibson Assembly"],"correct":2,"explanation":"정답 C: RNA splicing은 아닙니다."},
    {"type":"mc","question":"37. RNA 기반 유전자 조절에서 mRNA를 직접 분해하는 주요 RNA는?","options":["miRNA","siRNA","lncRNA","circRNA"],"correct":1,"explanation":"정답 B: siRNA입니다."},
    {"type":"mc","question":"38. 다음 중 BioBrick 부품의 조립에 사용되는 제한효소가 아닌 것은?","options":["EcoRI","XbaI","SpeI","BsaI"],"correct":3,"explanation":"정답 D: BsaI는 아닙니다."},
    {"type":"mc","question":"39. AND 게이트의 생물학적 구현 조건은?","options":["하나 입력만","입력 없음","두 입력 필요","항상 출력"],"correct":2,"explanation":"정답 C: 두 입력이 모두 필요합니다."},
    {"type":"mc","question":"40. CRISPR-Cas 시스템에서 적응 단계의 핵심은?","options":["Cas 발현","DNA 절단","바이러스 DNA 삽입","RNA 전사"],"correct":2,"explanation":"정답 C: 바이러스 DNA 삽입입니다."},
    {"type":"mc","question":"41. 유전자 발현을 실시간으로 관찰할 수 있는 방법은?","options":["Northern blot","Western blot","GFP 기반 형광 측정","전기영동"],"correct":2,"explanation":"정답 C: GFP 측정입니다."},
    {"type":"mc","question":"42. 합성생물학에서 사용되는 수학적 모델링 기법이 아닌 것은?","options":["ODE","Boolean Networks","RNA-seq","Stochastic Modeling"],"correct":2,"explanation":"정답 C: RNA-seq은 아닙니다."},
    {"type":"mc","question":"43. 피드백 루프 중 출력이 입력을 억제하는 방식은?","options":["양성","음성","에러 증폭","상보 억제"],"correct":1,"explanation":"정답 B: 음성 피드백입니다."},
    {"type":"mc","question":"44. 다음 중 '논리 회로' 구현과 관련 깊은 개념은?","options":["Enzyme cascade","BioBrick Registry","Boolean Logic","DNA methylation"],"correct":2,"explanation":"정답 C: Boolean Logic입니다."},
    {"type":"mc","question":"45. SBOL의 목적은 무엇인가?","options":["RNA 속도 측정","DNA 결합","부품 시각 표현","번역"],"correct":2,"explanation":"정답 C: 부품 시각 표현 표준화입니다."},
    {"type":"mc","question":"46. BioBrick 조립 방식의 큰 장점은?","options":["제한無","대규모","표준화","단백질 직접"],"correct":2,"explanation":"정답 C: 표준화된 모듈러 조립입니다."},
    {"type":"mc","question":"47. RBS 강도가 번역 효율에 미치는 영향은?","options":["강↑ 발↓","강↓ 발↑","강↑ 결합↑","무관"],"correct":2,"explanation":"정답 C: 결합↑으로 번역↑입니다."},
    {"type":"mc","question":"48. 코돈 최적화의 목적은?","options":["splicing↑","인자 활성","접힘 억제","번역 효율↑"],"correct":3,"explanation":"정답 D: 번역 효율 향상입니다."},
    {"type":"mc","question":"49. Terminator의 주요 기능은?","options":["번역 촉진","분해","전사 종료","결합"],"correct":2,"explanation":"정답 C: 전사 종료 역할입니다."},
    {"type":"mc","question":"50. Synthetic Oscillator의 기능은?","options":["절단","안정↑","주기 발현","삭제"],"correct":2,"explanation":"정답 C: 주기적 유전자 발현 유도입니다."},
    {"type":"mc","question":"51. '카운터' 장치의 주요 기능은?","options":["시간 단축","횟수 계수","억제","복제 차단"],"correct":1,"explanation":"정답 B: 신호 횟수 계수입니다."},
    {"type":"mc","question":"52. BioCAD 툴이 아닌 것은?","options":["TinkerCell","Clotho","GenoCAD","UniProt"],"correct":3,"explanation":"정답 D: UniProt은 데이터베이스입니다."},
    {"type":"mc","question":"53. RNAi 기전에서 mRNA를 절단하는 복합체는?","options":["miRISC","RISC","Drosha","Exportin"],"correct":1,"explanation":"정답 B: RISC입니다."},
    {"type":"mc","question":"54. 실험 전 예측 정확도를 높이는 도구는?","options":["BioBrick","CRISPRi","모델링","형광 단백질"],"correct":2,"explanation":"정답 C: 수학적 모델링입니다."},
    {"type":"mc","question":"55. Translation 조절에 관여하는 요소는?","options":["Promoter","Enhancer","RBS","Operon"],"correct":2,"explanation":"정답 C: RBS입니다."},
    {"type":"mc","question":"56. siRNA 치료제로 알맞지 않은 것은?","options":["Givosiran","Patisiran","Tamiflu","Onpattro"],"correct":2,"explanation":"정답 C: Tamiflu는 아닙니다."},
    {"type":"mc","question":"57. circRNA의 기능이 아닌 것은?","options":["번역","스펀징","억제","복제"],"correct":3,"explanation":"정답 D: DNA 복제는 아닙니다."},
    {"type":"mc","question":"58. SBOL 활용 이유는?","options":["RNA 서열 분석","형광 기록","시각적 회로 표현","돌연변이 탐지"],"correct":2,"explanation":"정답 C: 시각적 표현을 위해 사용됩니다."},
    {"type":"mc","question":"59. Tet-Off 시스템에서 tetracycline 존재 시 결과는?","options":["발현 활성화","억제 해제","tTA 결합","발현 억제"],"correct":3,"explanation":"정답 D: 발현이 억제됩니다."},
    {"type":"mc","question":"60. 합성생물학 계층적 설계에서 장치(Devices)는 어떤 기능을 하는가?","options":["단일 DNA 기능","부품 조합 기능","전체 유전체","단백질만 생성"],"correct":1,"explanation":"정답 B: 여러 부품 결합 기능 수행합니다."}, {
        "type": "mc",
        "question": "Orthogonal ribosome–mRNA systems are designed to…",
        "options": [
            "use the host ribosomes exclusively for engineered circuits",
            "recruit non‑standard nucleotides for translation",
            "operate independently of the cell’s native translation machinery",
            "degrade native mRNAs to free up ribosomes"
        ],
        "correct": 2,
        "explanation": "These systems run separately from the host’s own translation machinery."
    },
    {
        "type": "mc",
        "question": "In a stochastic gene expression model, increasing the transcription rate while holding translation constant will generally…",
        "options": [
            "decrease intrinsic noise (CV²) in protein levels",
            "increase extrinsic noise only",
            "shift the noise power spectrum to higher frequencies",
            "have no effect on noise"
        ],
        "correct": 0,
        "explanation": "Higher transcription lowers intrinsic noise by producing more mRNAs per protein."
    },
    {
        "type": "mc",
        "question": "A “toggle switch” circuit typically relies on which pair of regulatory elements?",
        "options": [
            "Two mutually activating promoters",
            "A sigma factor + anti‑sigma factor",
            "Two mutually repressing transcription factors",
            "An activator and a riboswitch"
        ],
        "correct": 2,
        "explanation": "Mutual repression between two repressors creates a bistable switch."
    },
    {
        "type": "mc",
        "question": "To minimize host burden when expressing a multi‑enzyme metabolic pathway, you would…",
        "options": [
            "maximize promoter strengths for every gene",
            "distribute expression across different plasmid copy numbers",
            "use a single strong ribosome binding site for all genes",
            "co‑express all enzymes as a fusion protein"
        ],
        "correct": 1,
        "explanation": "Spreading genes on distinct copy‑number plasmids balances resource usage."
    },
    {
        "type": "mc",
        "question": "A “quorum‑quenching” enzyme in a synthetic consortium serves to…",
        "options": [
            "amplify AHL signals for communication",
            "hydrolyze signaling molecules and avoid premature activation",
            "phosphorylate LuxR to activate gene expression",
            "fluorescently label quorum signals"
        ],
        "correct": 1,
        "explanation": "It degrades AHL to prevent unwanted quorum sensing."
    },
    {
        "type": "mc",
        "question": "In CRISPRa (CRISPR activation), a catalytically dead Cas9 (dCas9) is fused to…",
        "options": [
            "a repressor domain to knock down gene expression",
            "a nuclease to introduce double‑strand breaks",
            "a transcriptional activator to upregulate target genes",
            "a DNA methyltransferase to silence target promoters"
        ],
        "correct": 2,
        "explanation": "dCas9‑activator fusions recruit transcription machinery to upregulate genes."
    },
    {
        "type": "mc",
        "question": "An RBS Calculator predicts translation initiation rates by modeling…",
        "options": [
            "RNA polymerase rate constants",
            "folding free energy of mRNA around the start codon",
            "tRNA charging levels",
            "ribosome degradation kinetics"
        ],
        "correct": 1,
        "explanation": "It computes mRNA secondary‑structure free energies near the RBS region."
    },
    {
        "type": "mc",
        "question": "Directed evolution of an enzyme in vivo often uses…",
        "options": [
            "site‑specific recombinases to shuffle protein domains",
            "error‑prone PCR plus a high‑throughput selection system",
            "a rational redesign based on crystal structures only",
            "CRISPR‑mediated single‑point knockout"
        ],
        "correct": 1,
        "explanation": "Error‑prone PCR libraries with selection/screening is the standard approach."
    },
    {
        "type": "mc",
        "question": "A “metabolic valve” in a synthetic pathway refers to…",
        "options": [
            "an RNA aptamer controlling enzyme localization",
            "an inducible protein degradation tag that toggles flux",
            "a permanently deleted gene to reroute metabolism",
            "a chemical inhibitor of the first enzyme in the pathway"
        ],
        "correct": 1,
        "explanation": "Degradation tags allow dynamic on/off control of key enzymes."
    },
    {
        "type": "mc",
        "question": "In a two‑cell synthetic consortium where one strain supplies an essential metabolite, this is an example of…",
        "options": [
            "auxotrophy",
            "cross‑feeding mutualism",
            "quorum sensing",
            "bet–hedging"
        ],
        "correct": 1,
        "explanation": "Each strain depends on the other’s metabolite, forming mutualistic cross‑feeding."
    },
    {
        "type": "mc",
        "question": "The main advantage of using a phage‑derived RNA polymerase (e.g., T7 RNAP) in circuits is…",
        "options": [
            "its orthogonality and strong, tunable expression",
            "higher fidelity than host RNAP",
            "ability to transcribe in the absence of NTPs",
            "inducing native stress responses"
        ],
        "correct": 0,
        "explanation": "T7 RNAP works independently of host RNAP and provides high expression."
    },
    {
        "type": "mc",
        "question": "A ribozyme‑based biosensor can detect small molecules by…",
        "options": [
            "changing its fluorescence upon ligand binding",
            "folding into an active cleavage conformation only in the presence of ligand",
            "inhibiting translation of a reporter protein by occupying the RBS",
            "recruiting RNase III"
        ],
        "correct": 1,
        "explanation": "Ligand binding induces a cleavage‑competent fold in the ribozyme sensor."
    },
    {
        "type": "mc",
        "question": "To achieve dynamic oscillations with tunable frequency, one might implement…",
        "options": [
            "a single negative feedback loop with time delay",
            "a toggle switch under constitutive promoters",
            "a metabolic pathway with irreversible steps",
            "a two‑component sensor kinase"
        ],
        "correct": 0,
        "explanation": "Delayed negative feedback is the minimal motif for tunable oscillations."
    },
    {
        "type": "mc",
        "question": "Synthetic epigenetic control in bacteria has been demonstrated by…",
        "options": [
            "engineering histone‑like proteins with reader/writer domains",
            "site‑specific DNA methylation via dCas9‑DNMT fusion",
            "overexpressing native histone deacetylases",
            "introducing eukaryotic nucleosomes"
        ],
        "correct": 1,
        "explanation": "dCas9‑DNMT fusions deposit methyl marks at target loci in bacteria."
    },
    {
        "type": "mc",
        "question": "The principle of retro‑biosynthesis in pathway engineering involves…",
        "options": [
            "running in vitro reactions in reverse to obtain cofactors",
            "designing metabolic routes backward from target molecule to central metabolites",
            "reversing gene order on operons for increased expression",
            "employing reverse transcriptase to duplicate pathways"
        ],
        "correct": 1,
        "explanation": "Retro‑biosynthesis starts from the end product and works back to precursors."
    },
    {
        "type": "mc",
        "question": "A minimal cell chassis for synthetic biology aims to…",
        "options": [
            "remove all plasmids and phages only",
            "delete nonessential genes to reduce resource competition",
            "contain only one ribosomal RNA operon",
            "overexpress stress‑response genes"
        ],
        "correct": 1,
        "explanation": "Eliminating nonessential genes frees up resources for engineered functions."
    },
    {
        "type": "mc",
        "question": "Optogenetic control of gene expression is achieved through…",
        "options": [
            "light‑activated dimerization of transcription factors",
            "RNA aptamers that fluoresce under UV",
            "caged nucleotides incorporated by polymerases",
            "CRISPR knockouts only at night"
        ],
        "correct": 0,
        "explanation": "Photosensitive domains drive TF dimerization under specific wavelengths."
    },
    {
        "type": "mc",
        "question": "In CRISPR gene drives, the drive efficiency is limited by…",
        "options": [
            "the half‑life of Cas9 protein in the nucleus",
            "resistance alleles arising from nonhomologous end joining",
            "promoter leakiness in germ cells",
            "guide RNA secondary structure only"
        ],
        "correct": 1,
        "explanation": "NHEJ repairs create resistant alleles that block further drive."
    },
    {
        "type": "mc",
        "question": "Xenobiology extends the genetic code by…",
        "options": [
            "using quadruplet codons or noncanonical amino acids",
            "modifying ribosomes to read RNA 5’ cap structures",
            "inserting archaeal tRNAs into bacteria",
            "deleting endogenous tRNA genes"
        ],
        "correct": 0,
        "explanation": "Orthogonal codons and novel amino acids expand the coded repertoire."
    },
    {
        "type": "mc",
        "question": "A synthetic “memory” circuit that records transient events in DNA uses…",
        "options": [
            "recombinases to flip DNA segments permanently",
            "dCas9 to block transcription",
            "two‑hybrid interactions to produce fluorescent aggregates",
            "riboswitches coupled to cell division"
        ],
        "correct": 0,
        "explanation": "Site‑specific recombinases invert or excise sequences, encoding a permanent record."
    }
]

# 세션 초기화
if 'index' not in st.session_state:
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.submitted = False

# 현재 질문
q = questions[st.session_state.index]

st.markdown(f"### 문제 {st.session_state.index+1} / {len(questions)}")
st.markdown(f"> **{q['question']}**")

# 입력 폼
with st.form(key=f"form_{st.session_state.index}"):
    if q['type'] == 'mc':
        user_choice = st.radio("선택지", q['options'])
    else:
        user_choice = st.text_area("주관식 답안")
    submit_btn = st.form_submit_button("제출")

# 제출 처리
if submit_btn and not st.session_state.submitted:
    if q['type'] == 'mc' and q['options'].index(user_choice) == q['correct']:
        st.session_state.score += 1
    if q['type'] == 'sa' and similarity(user_choice.lower().strip(), q['answer'].lower().strip()) >= 0.9:
        st.session_state.score += 1
    st.session_state.submitted = True

# 해설 표시
if st.session_state.submitted:
    explain = q['explanation'] if q['type']=='mc' else q['answer']
    st.success(f"**해설:** {explain}")

# 항상 보여질 이전/다음 버튼
col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("◀️ 이전") and st.session_state.index > 0:
        st.session_state.index -= 1
        st.session_state.submitted = False
with col3:
    if st.button("다음 ▶️") and st.session_state.index < len(questions)-1:
        st.session_state.index += 1
        st.session_state.submitted = False

# 최종 결과
if st.session_state.index == len(questions)-1 and st.session_state.submitted:
    st.markdown("---")
    st.markdown(f"## 🎉 퀴즈 완료! 점수: {st.session_state.score} / {len(questions)}")
    st.markdown(f"**정답률: {(st.session_state.score/len(questions)*100):.1f}%**")
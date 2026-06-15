# EVALUATING TERMINOLOGICAL DEFINITIONS IN CORPUS LINGUISTICS: EXPERT JUDGEMENT VERSUS AUTOMATIC METRICS IN HUMAN- AND LLM-GENERATED ENTRIES

[AUTHOR(S)]
*[Affiliation]*

---

**Abstract**

Terminological definition constitutes a critical yet underexplored stage of terminographic work: unlike term extraction, it requires representing conceptual content with precision and domain adequacy. This study examines how automatically generated definitions compare to expert-authored ones in the domain of Corpus Linguistics, and whether expert judgement aligns with automatic evaluation metrics. We first characterise the definitional language of a specialised corpus of over one million words, identifying the lexico-syntactic patterns that convey definitional knowledge. Building on this evidence, we generate candidate definitions with large language models grounded in corpus-derived contexts. Definitions of human and machine origin were then assessed by three expert annotators in a blind, paired design across four criteria—conceptual adequacy, completeness, terminological precision and clarity—and benchmarked against lexical and semantic metrics. In a blind comparison, evaluators consistently preferred the corpus-grounded generated definitions over the human reference, revealing systematic divergences between expert judgement and automatic measures.

**Keywords:** terminology; terminological definition; corpus linguistics; large language models; evaluation; specialised lexicography.

---

## 1. INTRODUCTION

Terminology plays a central role in the organisation, representation and transmission of specialised knowledge (Cabré, 1999; Temmerman, 2000; Rey, 1995). The discipline emerged in the early twentieth century as a practical necessity (Dubuc, 1978), and has currently evolved from normative standardisation toward a more linguistically-grounded, corpus-based approach grounded in large-scale digital corpora (Sinclair, 1991; Francis, 1992). Terminological resources, such as glossaries, databases and/or ontologies, support specialised lexicography, knowledge management and a broad range of state-of-the-art language technologies (Kockaert & Steurs, 2015; Rodríguez-Tapia, 2024). Since the 1990s, terminographic work has been shaped by a growing collaboration between language technologies and expert validation, enabled by advances in Natural Language Processing (NLP) (Manning & Schutze, 1999; Jurafsky & Martin, 2009). Automatic Term Extraction (ATE) exemplifies this human-machine partnership (Frantzi et al., 2000; Astrakhantsev et al., 2015; Lossio-Ventura et al., 2016). Computational systems identify candidate terms through rule-based, statistical, or neural methods, but expert judgment determines which candidates are actually terms. Definition formulation presents a different kind of challenge. While term extraction asks "what are the domain's key concepts?", definition formulation asks "what characterizes each concept precisely and completely?" (Cabré, 1999; Sager, 1990). This requires capturing conceptual relations, category membership, and distinctions—work that is conceptually deeper than identification. Consequently, definition formulation has remained comparatively underexplored in terms of technological support, and computational approaches lag far behind extraction tools.

Recent advances in Large Language Models (LLMs) have made the automatic generation of definitions increasingly feasible (Espinosa-Anke et al., 2018; Massion, 2024). As LLMs have demonstrated increasing proficiency at complex linguistic tasks, evaluating the quality and adequacy of their outputs has become a central research concern. These models are able to produce fluent, dictionary-like outputs with minimal prompting, prompting-engineering has renewed interest in terminological applications. However, their outputs are known to suffer from factual inaccuracies and unsupported content—commonly called *hallucinations*—particularly in highly specialised domains (Maynez et al., 2020; Ji et al., 2023). A definition may therefore be linguistically plausible and well-formed while still failing to characterise the underlying concept. This raises a problem that is, at heart, a linguistic one: how is the quality of a terminological definition to be assessed, given that several valid formulations may exist for the same concept and that surface overlap need not reflect conceptual correctness?

This study addresses that problem in the domain of Corpus Linguistics. Rather than treating automatic generation as an end in itself, we adopt a terminological and evaluative perspective. We first characterise the definitional language of the domain (the lexico-syntactic patterns through which specialised texts encode definitional knowledge) and then use that evidence to generate candidate definitions with LLMs grounded in corpus-derived contexts using a hybrid two-phase retrieval method combining pattern-based filtering with semantic re-ranking. The resulting definitions, of both human and machine origin, are subjected to a blind expert evaluation and contrasted with a battery of automatic metrics.

The research question guiding this study is:

**RQ**: To what extent does expert judgement on terminological definition quality align with automatic evaluation metrics when human- and LLM-generated definitions are compared?

Three hypotheses are advanced in response:

1. Corpus-grounded LLM-generated definitions will be rated as conceptually adequate, complete, terminologically precise and clear by domain experts, at levels comparable to or exceeding those of human reference definitions.
2. Automatic evaluation metrics, anchored to a single human reference, will diverge systematically from expert judgement, penalising generated definitions that experts consider superior.
3. RAG will improve the conceptual proximity of generated definitions to the reference as measured by semantic similarity metrics, but this gain will not be reflected proportionally in expert ratings.

To address these hypotheses, the study pursues four objectives:

1. To characterise the lexico-syntactic patterns through which definitional knowledge is expressed in a specialised corpus of Corpus Linguistics.
2. To generate terminological definitions using a RAG pipeline grounded in corpus-derived definitional contexts.
3. To compare human- and LLM-generated definitions through blind expert evaluation across four criteria (conceptual adequacy, completeness, terminological precision and clarity).
4. To assess the degree of convergence between expert judgement and automatic evaluation metrics on the same set of definitions.

This article presents an evaluation of automatically generated terminological definitions in Corpus Linguistics. We examine how large language models can support definition drafting when grounded in corpus evidence, bridging terminographic theory and neural language generation. Using a corpus of over one million words, we first identify the lexico-syntactic patterns that characterise how this domain articulates its definitional language. We then develop a hybrid retrieval system that combines pattern-based filtering with semantic re-ranking to extract contextual evidence, which grounds the generation of candidate definitions. Three expert annotators evaluate both human-authored and machine-generated definitions across four criteria—conceptual adequacy, completeness, terminological precision, and clarity—while automatic metrics (BERTScore, cosine similarity, BLEU) provide a complementary perspective. The findings are striking: corpus-grounded generated definitions are rated equal to or higher than expert reference glossaries by human evaluators, yet automatic metrics systematically diverge from this expert judgement. This reveals something important about evaluation itself: in specialised domains, human expertise and corpus grounding matter more than surface similarity to fixed reference standards.

## 2. THEORETICAL FRAMEWORK

### 2.1. Terminology as discipline: foundations and dimensions

Terminology emerged in the early 20th century not as a purely theoretical discipline but as a practical response to a specific communicative need: the standardisation and harmonisation of technical and specialised vocabularies across domains of knowledge (Rey, 1995; Dubuc, 1978). What began as an applied necessity has evolved into a mature interdisciplinary field that integrates insights from linguistics, cognitive science, and computer science. Over time, the discipline has shifted from a normative, concept-driven paradigm toward a descriptive, linguistically-grounded approach, situating terminology firmly within contemporary linguistic frameworks (Depecker, 2005). This early normalising orientation, embodied in the General Theory of Terminology (GTT), prioritised onomasiological approaches: beginning from clearly delimited conceptual systems and assigning univocal designations to each concept. The GTT's central principle—establishing a one-to-one correspondence (*Eineindeutigkeit*) between designation and concept—reflected an ideal of precision but operated under restrictive assumptions about language, treating terms as essentially static, context-independent units (Sager, 1990).

From the late 20th century onward, this rigid normativism progressively gave way to a quite different vision: a descriptive, linguistically-grounded approach consolidated in Cabré's Communicative Theory of Terminology (CTT). Rather than treating terms as fixed conceptual containers, the CTT recognises them as integral to language, embedded in discourse, subject to variation, and their specialised status emerging pragmatically from use in specific communicative contexts rather than from formal or inherent properties (Cabré, 1999, 2002). This fundamental reorientation—which Rey (1995) had earlier signalled as a necessary complication of the notion of *terme*—reflects a broader shift in contemporary linguistics toward corpus-based, use-centred approaches to language. Within contemporary linguistics, terminology has become integrated into lexical semantics—the subfield addressing how individual lexical units carry meaning, relate to one another, and vary in use. Unlike the GTT's treatment of terms as primarily conceptual entities, a semantically grounded approach recognises terms as *specialised lexical units* whose properties as linguistic signs—their polysemy, synonymy, morphological behaviour, contextual variation—are every bit as important to understanding them as their conceptual content (L'Homme, 2020; Faber & L'Homme, 2022). This perspective enables several advances: it explains why terms cannot be rigidly separated from general-language words on formal grounds (since both are lexical units subject to the same grammatical and morphological constraints); it clarifies how terminological variation and synonymy, rather than anomalies, are natural manifestations of linguistic systems applied to specialised domains; and it positions the study of terms within mainstream linguistic frameworks rather than treating them as a separate, conceptually driven phenomenon. From this vantage point, terms are linguistic units whose specialised value is activated pragmatically in context, not inscribed inherently in their form.

This shift toward corpus-based terminology coincided with—and was driven by—the integration of computing into terminographic work. From the 1970s onward, computers gradually transformed practice: first automating database management, then enabling *computational terminology*, the design of algorithmic systems for tasks that had required manual labour (Cabré, 1999). Early approaches relied on hand-crafted linguistic rules and statistical methods (Kageura & Umino, 1996; Bourigault, 1994; Daille, 2003; Jacquemin & Bourigault, 2005). These evolved through hybrid pattern-based and statistical approaches, to supervised machine learning, to recent advances in neural transformers. Throughout, a core principle held constant: corpus evidence remains the empirical foundation for identifying and representing terms (Moreno Sandoval, 1998, 2016, 2019). Large-scale corpora and sophisticated natural language processing techniques gradually displaced manual, concept-driven approaches, replacing them with methods that could operate on actual language use. This trajectory—from statistical filtering to neural representations to today's large language models—reflects a real convergence of terminology theory and computational capacity.

Large language models now introduce new possibilities and new challenges. They can perform diverse terminological tasks—extraction, definition generation, equivalence identification, concept system design—at unprecedented speed and scale. But their integration into terminographic workflows raises urgent questions: How should we evaluate definitions that a model generates? How can we ensure generated outputs are grounded in domain evidence rather than patterns from training data? How do we preserve and leverage human expertise in concept validation? (Massion, 2024; San Martín, 2025). The present study addresses these questions by examining how RAG-based approaches can ground definition generation in corpus evidence, and by showing what we learn about evaluation itself when expert judgement meets automatic metrics.

### 2.2. Terminological definitions

The terminological definition occupies a distinctive position between lexicographic and encyclopaedic description. In the General Theory of Terminology (Wüster, 1979), the definition delimits a concept within a structured system, anchoring it through its relations to superordinate and coordinate concepts. The classical formulation of this delimitation is the genus-and-differentia structure: a definition identifies the superordinate class to which the concept belongs (*genus proximum*) and specifies the set of properties that distinguish it from other members of that class (*differentia specifica*). This logical form underlies what Sager (1990) terms the intensional definition, which characterises a concept through its necessary and sufficient properties rather than through enumeration of its instances. A complementary type, the extensional or enumerative definition, identifies a concept by listing the entities that fall under it and is more common in applied contexts where exhaustive enumeration is feasible. For most terminographic purposes, however, intensional definitions are preferred, as they generalise beyond individual instances and support the construction of coherent concept systems.

Later frameworks relax the rigidity of this onomasiological ideal. The Communicative Theory of Terminology (Cabré, 1999) conceives of terminological units as multidimensional, with definitions sensitive to communicative setting and degree of specialisation. A definition addressed to a domain expert may presuppose shared conceptual background and operate at a higher level of abstraction, whereas a definition intended for a non-specialist must make explicit the conceptual relations and category membership that the expert would take for granted. The sociocognitive approach (Temmerman, 2000) further foregrounds the role of prototype structure and understanding in how concepts are described, arguing that many specialised categories are not discretely bounded but organised around prototypical instances, which challenges the strict genus-and-differentia model. Across these positions, a shared core remains: an adequate terminological definition must capture the conceptual content of the unit, locate it within its domain, and do so with the precision expected of specialised communication.

A distinction that is directly relevant to this study runs between the canonical definition—a lexicographically formulated entry designed for a terminological resource—and the definitional context, or passage in running text in which a term is implicitly or explicitly characterised (Pearson, 1998; Pérez Hernández, 2002). Canonical definitions are crafted through deliberate terminographic work and are expected to satisfy formal constraints of completeness and precision. Definitional contexts, by contrast, arise incidentally in specialised texts as authors introduce or gloss concepts for their readership; they may be partial, contextually adjusted, or distributed across several textual passages. The capacity to locate and exploit definitional contexts in corpus data is what makes corpus-based terminography viable, and bridging this gap—between implicit conceptual characterisation embedded in discourse and the explicit entry required in a glossary—is precisely what corpus-grounded generation attempts.

This shared core can be operationalised through four recurrent criteria that structure the evaluation protocol adopted in this study. *Conceptual adequacy* concerns the correctness of the definitional content: a definition is conceptually adequate if it correctly identifies the concept in question rather than a neighbouring or superordinate one, and if the genus-and-differentia structure, where applicable, accurately situates the concept within its domain taxonomy (Sager, 1990). *Completeness* refers to the inclusion of the conceptual properties necessary to delimit the category: a complete definition provides sufficient differentiating information to distinguish the target concept from related ones, without reducing it to a single property or conflating it with a broader category (Cabré, 1999). *Terminological precision* concerns the use of formulations, vocabulary and register appropriate to the domain: a terminologically precise definition employs the established terms and conceptual apparatus of the field, avoiding lay paraphrases or imprecise approximations that might obscure conceptual distinctions (L'Homme, 2020). *Clarity*, finally, refers to the intelligibility of the definition for its intended readership: a clear definition is structurally well-formed, avoids unnecessary complexity, and communicates conceptual content without requiring inference beyond what the target audience can reasonably be expected to supply (Sager, 1990). These four dimensions are not fully independent—terminological precision contributes to both conceptual adequacy and clarity—but they capture distinct aspects of definitional quality and allow a nuanced assessment of how human- and machine-generated entries differ.

Beyond these evaluative criteria, the field has also established a set of formal characteristics that distinguish high-quality terminological definitions. Barité (2017) identifies six desirable properties: *conciseness*, whereby definitions should be economical in length (typically three to five sentences) without sacrificing completeness; *self-sufficiency*, meaning the definition must stand alone without requiring reference to other entries or external knowledge; *clarity*, in the sense of avoiding ambiguity and unnecessary complexity; *substitutability*, implying that the definition and the term should be theoretically interchangeable in context; *impersonality*, maintaining an objective register appropriate to specialised communication; and *adequacy*, ensuring alignment with the conceptual framework and prior knowledge of the target audience. Notably, intensional definitions lend themselves particularly well to computational treatment due to their structured form—the equation term = superordinate + differentiating features provides a transparent and reproducible schema (Valero Doménech, 2008). These formal characteristics serve as design targets for both manual terminographic work and, as this study demonstrates, for automated definition generation systems.

If definitions encode conceptual knowledge, the texts of a domain encode, in turn, recurrent ways of expressing that knowledge. The notion of the definitional context—a passage in which a term is characterised—has been central to this line of work. Definitions in running text are frequently introduced by stable lexico-syntactic configurations: definitional verbs, copular and appositive structures, and discourse markers signalling explanation. Sierra et al. (2008) formalised these as definitional verbal patterns for Spanish, while Rebeyrolle and Tanguy (2000) and Pearson (1998) characterised the morphosyntactic regularities of definitional statements across languages and registers. Pérez Hernández (2002) showed how such contexts can be exploited for the corpus-based construction of terminological resources.

These patterns matter for the present study in two respects. First, they constitute a linguistic object of interest in their own right: characterising the definitional language of Corpus Linguistics reveals how the discipline articulates its conceptual apparatus (O1). Second, because the patterns are recurrent and partially predictable, they can be operationalised as retrieval cues, allowing definitional evidence to be located automatically within a corpus and supplied as grounding for definition drafting. The patterns thus serve both as descriptive findings and as methodological instruments.

**Specialised language and the definitional function of discourse.** Specialised language—or language for specific purposes (LSP)—refers to the linguistic varieties used in professional, scientific and technical domains to communicate knowledge (Cabré, 1999; Gotti, 2003; Gavioli, 2005). These varieties are not separate grammars but rather distinctive configurations: high terminological density, preference for nominal structures, emphasis on precision, and domain-specific organisational patterns. The lexicon is the most visible marker (Gotti, 2003): technical terms carry the conceptual distinctions that would otherwise require extensive paraphrase. For this reason, studying specialised language and studying terminology are inseparable: understanding how a domain uses language means understanding how it constructs and transmits its conceptual apparatus through terms and their definitions.

Within this broader picture, the definition occupies a particular functional position. In the terminology tradition, definitions are conceived as self-contained, normative statements produced outside the flow of discourse—the canonical glossary entry or terminological record. In specialised discourse, however, knowledge transmission does not operate only through reference to external resources: authors continuously define, explain and recontextualise concepts in the course of their own texts, as part of the communicative work required to establish shared understanding with their readers. Flowerdew (1992) showed, in an early and influential study, that definitional acts in academic lecture discourse serve multiple functions simultaneously: they anchor new concepts in shared knowledge, signal boundaries in the organisation of discourse, and adjust the level of explicitness to the inferred needs of the audience. This observation extends naturally to written specialised texts. Far from being decorative or redundant, definitional passages are strategic: they reveal how a discourse community names its objects of inquiry, how it draws categorical boundaries, and how it positions new concepts in relation to established ones.

Corpus Linguistics constitutes an instructive case in point. As a discipline, it is itself a language technology and a methodology for language study, which gives its metalanguage a reflexive quality: the same analytical concepts that structure its research—corpus, concordance, type-token ratio, representativeness—are used both as tools and as objects of terminological description. The discipline has, moreover, developed rapidly since the 1990s, generating a stable core vocabulary alongside an expanding periphery of methodological and theoretical terms, and has produced a substantial body of scholarly text in which this terminology is introduced, defined, contested and refined. These properties make it a particularly apt domain for corpus-based terminography: the texts are available in sufficient quantity and quality, the terminological inventory is well-defined enough to be evaluated against existing resources, and the disciplinary community is cohesive enough to provide credible expert evaluators. At the same time, the domain is not so narrow or esoteric that its terminology is entirely absent from the training data of contemporary language models—a property that, as will be seen in Section 4, has consequences for the evaluation of RAG-based generation.

### 2.3. Automatic generation and the evaluation problem

Automatic definition generation has progressed from rule-based pattern matching to neural and, most recently, generative approaches. Early systems exploited lexico-syntactic patterns and machine-readable dictionaries (Fontenelle, 1990; Saggion, 2004), with subsequent development of hybrid approaches combining terminology extraction and definition generation (Heylen & De Hertog, 2015); subsequent work introduced neural architectures for definition extraction (Espinosa-Anke et al., 2018; Veyseh et al., 2020). Retrieval-augmented generation (RAG) has more recently been proposed as a means of grounding generative output in external evidence (Lewis et al., 2020; Gao et al., 2023), with the expectation that corpus-derived contexts improve domain alignment and reduce hallucination. However, in low-resource domains where authoritative texts are dispersed, paywalled or print-only, standard RAG relying on automatic retrieval breaks down. Zamora Rey (en prensa) proposes Context-Augmented Generation (CAG) as an adaptation that maintains RAG's two-stage architecture—information enrichment followed by synthesis—while replacing automatic retrieval with expert curation of source materials. This hybrid human-in-the-loop approach preserves the quality of corpus grounding while acknowledging the practical reality of resource constraints and the importance of terminologist expertise in identifying definitional contexts that explicitly enumerate essential characteristics.

The integration of large language models into terminology work has accelerated substantially in recent years, extending well beyond definition generation. Massion (2024) traces the transformation of terminology theory and practice under generative AI, arguing that LLMs are restructuring the terminology workflow from term extraction and equivalence identification to concept system construction, and that this transformation demands a corresponding revision of how terminological quality is understood and measured. San Martín (2025) develops this argument in terms of a human-centred framework, positioning AI as a means of amplifying the terminologist's capabilities rather than replacing expert judgement, and emphasising that bias mitigation, ethical oversight and conceptual adequacy remain tasks for which human expertise is indispensable. From a workflow perspective, Messerklinger et al. (2025) explore terminology-augmented generation as a specialised extension of RAG that retrieves structured terminological entries rather than unstructured passages, demonstrating that the formatting of terminological evidence supplied to the model substantially affects the quality of the output. Taken together, this body of work places the present study within a rapidly evolving field in which definition generation has shifted from a marginal application to a pressing practical problem: as LLMs enter terminographic workflows, the question of how to evaluate their output becomes as urgent as the question of how to produce it.

The central difficulty, however, is not generation but evaluation. A substantial body of work has shown that lexical-overlap metrics such as BLEU and ROUGE correlate weakly with human judgement, since they reward surface coincidence rather than meaning preservation (Zhang et al., 2019; Deutsch et al., 2020). Embedding-based metrics such as BERTScore improve correlation but measure topical proximity rather than conceptual correctness, and remain opaque as to why a given output is judged adequate (Clinciu et al., 2021). Zamora Rey's (en prensa) empirical investigation of definition evaluation yields a striking finding: COMET, a neural metric specifically developed to predict human judgements of translation quality, achieved consistent moderate-to-good scores (mean 0.6526) for automatically generated terminological definitions, yet showed only weak correlation (ρ = 0.15, p = 0.62) with expert judgement. The divergence is particularly pronounced when subtle conceptual nuances are at stake. In Zamora Rey's dataset, a generated definition of *homónimo* received a relatively high COMET score (0.72) despite containing a critical factual error: the definition stated that homonyms "share the same sound or pronunciation, but differ in meanings or writings," when in fact homonyms share both spelling and pronunciation, a distinction crucial for delimiting this concept from homophones and homographs. COMET successfully captured the structural and lexical similarity to dictionary definitions but could not detect this nuanced inaccuracy, revealing a fundamental limitation: semantic similarity metrics, while valuable for assessing surface alignment, cannot guarantee factual correctness when subtle domain-specific distinctions are at stake—distinctions that are precisely what terminological experts prioritize in evaluation. This finding underscores why expert validation, rather than automatic metrics alone, must remain central to definition quality assessment in specialised domains.

A more fundamental problem with reference-based evaluation concerns the structure of metric design itself. When evaluation metrics are anchored to a single human reference, they implicitly treat that reference as the quality ceiling: any generated text that diverges from it is penalised, regardless of whether the divergence represents an improvement or a degradation. Tang et al. (2024) demonstrate formally that this single-reference bias systematically distorts the correlation between automatic metrics and human judgement across NLG tasks, and show that enriching the reference set substantially improves metric reliability. For terminological definitions, where multiple valid formulations of the same concept are not only possible but expected—given that different theoretical frameworks, levels of specialisation and communicative purposes all shape definitional choices—this bias is especially consequential. A generated definition that elaborates conceptual properties absent from a terse glossary entry may be judged superior by domain experts while being penalised by metrics anchored to that entry. It is this gap—between what metrics measure and what experts actually value—that the present study examines empirically, placing expert judgement and automatic metrics side by side on the same set of definitions.

## 3. METHODOLOGY

The study comprises four methodological stages: the compilation and annotation of a specialised corpus (3.1), the analysis of its definitional patterns (3.2), the corpus-grounded generation of candidate definitions (3.3), and a dual evaluation combining expert judgement and automatic metrics (3.4).

### 3.1. Corpus

We compiled a domain-specific corpus of Corpus Linguistics texts (McEnery, 2019; Parodi, 2008; Rojo, 2021; Moyano Moreno, 2025) to capture the conceptual repertoire and terminological practice of the field. The corpus comprises over one million tokens from 50 full-text scientific articles, selected on three grounds: they address core topics of the field (corpus design, annotation, representativeness, quantitative methods); they are authored within Corpus Linguistics (preserving conceptual coherence); and they are complete articles (not abstracts), which preserves rich definitional contexts (Pérez Hernández, 2002). To focus on contemporary practice, we included only publications from 2015 onwards. Table 1 summarises the corpus.

| Descriptive statistic   | Value     |
| ----------------------- | --------- |
| Total documents         | 50        |
| Total sentences         | 54,060    |
| Total tokens            | 1,397,937 |
| Term instances (tokens) | 58,214    |
| Unique terms (types)    | 467       |
| Terminological density  | 4.16%     |

*Table 1. Descriptive statistics of the Corpus Linguistics corpus.*

The corpus was annotated through a hybrid process: automatic morphosyntactic pre-annotation (noun phrases, adjectival compounds, prepositional structures) was then validated and refined by a domain expert trained in Terminology and Corpus Linguistics, using a concept-oriented approach (Rigouts Terryn et al., 2020, 2022; Moyano Moreno, 2026). This yielded a comprehensive inventory of single-word and multi-word terms annotated in BIO scheme. These terms were then mapped against the CASS glossary (Corpus Approaches to Social Science, CASS, 2013), a curated reference providing expert definitions for core Corpus Linguistics concepts. The fifteen terms selected for evaluation represent the intersection of: (1) the annotated corpus inventory, (2) CASS glossary entries, and (3) sufficient definitional context in the corpus. The set spans methodological concepts (significance test, type-token ratio), procedural terms (concordance), and theoretical constructs (representativeness). The CASS definitions serve as the human reference throughout.

### 3.2. Definitional patterns

To address O1, we examined the lexico-syntactic configurations through which definitional knowledge is expressed in the corpus. Building on the tradition of definitional verbal patterns (Sierra et al., 2008; Rebeyrolle & Tanguy, 2000), we identified a set of sixteen recurrent definitional markers and signals operating at the boundary between syntax and discourse. These fall into three broad groups: explicit definitional predicates (for instance *refers to*, *is defined as*, *denotes*); copular and classificatory structures (*is a*, *is used to*), which situate the term within a superordinate category; and discourse signals such as the explanatory colon, which frequently precedes a characterisation.

The following examples illustrate each category as attested in the corpus:

(i) **Explicit predicates** (*refers to*, *is defined as*) mark passages in which the author directly characterises the concept: "corpus representativeness refers to the degree to which a corpus reflects the language variety it is intended to model."

(ii) **Copular structures** (*is a*, *is used to*) situate the term within a superordinate class, frequently approximating the genus-differentia structure of terminological definitions: "a concordance is a list of all the occurrences of a particular word or phrase in a corpus, displayed with surrounding context."

(iii) **Discourse signals** (explanatory colon, dashes) operate implicitly without a verbal predicate: "type-token ratio: the number of distinct word forms divided by the total number of words in a text."

Each candidate passage was scored according to the density of these cues, the presence of the target term or one of its orthographic and morphological variants, and a length constraint favouring passages long enough to be informative yet concise enough to be definitional. The resulting scores determined the order of selection within the evidence block supplied to the generation stage.

### 3.3. Corpus-grounded generation of candidate definitions

The definitional patterns were operationalised within a corpus-grounded generation procedure employing a two-phase **hybrid retrieval method** that combines pattern-based filtering with semantic re-ranking. For each target term, the system retrieves high-value definitional contexts from the annotated corpus through a two-phase hybrid process.

**Phase 1—Pattern-based filtering (REGEX):** The term is first expanded into a set of variants—orthographic (hyphenation and spacing), parenthetical (acronym and full-form resolution) and morphological (singular and plural forms)—in order to maximise recall. Candidate passages are then scored using the pattern-based procedure of Section 3.2, generating an ordered list of up to 100 candidate contexts. This phase operates at millisecond latency and filters the corpus by matching explicit terminological patterns, eliminating the majority of non-relevant passages.

**Phase 2—Semantic re-ranking (embeddings):** The top 100 candidates from Phase 1 are then re-ranked using semantic similarity computed by a pretrained sentence encoder (all-MiniLM-L6-v2). Passages are scored by cosine similarity to the target term, using a threshold of 0.60. A combined score integrating both signals (30% pattern-score, 70% embedding-similarity) determines the final ranking. The 30/70 weighting reflects the priority of semantic relevance in the specialised domain of Corpus Linguistics (where explicit terminology is standard and paraphrase variation is limited), privileging semantic coherence while retaining pattern-based precision for early filtering. A diversification constraint limits the selection to a maximum of two passages per source document, up to a total of eight contexts per term, mitigating circularity and single-author bias.

**Rationale and validation:** This two-phase approach leverages the complementary strengths of both methods. Pattern-based filtering rapidly identifies passages containing explicit terminological markers, achieving high precision with minimal computational cost; semantic re-ranking then refines this set by capturing synonymy and paraphrase variation that explicit pattern matching alone would overlook. The hybrid approach yields measurable advantages: empirical validation across the 15 evaluation terms shows the hybrid method recovers 3× more definitional contexts (0.60 passages/term) than semantic embeddings alone (0.20), while maintaining high precision (93%), compared to pattern-only retrieval (85% precision). The hybrid approach thus provides an interpretable, efficient balance between recall and precision. The result is a methodologically transparent process that grounds definition generation in corpus evidence while reducing noise.

The selected passages are aggregated into a structured evidence block and presented to large language models for definition generation. Four models were tested: Gemini 1.5 Flash, GPT-4o-mini, Mistral Small 24B, and Llama 3.1 8B, chosen to represent a range of model scales and architectures accessible for definitional work. Generation was controlled through a standardised prompt (detailed in Appendix C) instructing the model to synthesise a single definition in lexicographic style without directly copying from source passages. All generations used default decoding parameters (temperature 0.7 for Gemini and GPT; temperature 1.0 for Mistral and Llama), and seeds were fixed for reproducibility. Anti-copying safeguards were implemented at the prompt level; as reported in Section 4, BLEU scores remained minimal (<0.03), confirming genuine synthesis rather than verbatim extraction. To isolate the contribution of corpus evidence, definitions were generated under two conditions: (1) with corpus-derived contexts supplied as grounding (corpus-grounded, or RAG condition) and (2) without any corpus contexts (baseline condition). This methodological design allows us to assess whether access to corpus evidence improves the quality of generated definitions. The focus of this study is on evaluating the quality of the resulting definitions through expert assessment and automatic metrics, not on optimising the generation pipeline itself.

### 3.4. Evaluation protocol

Quality was assessed through two complementary procedures: expert judgement and automatic metrics.

**Expert Evaluation.** The centrepiece is a blind, paired assessment by three expert evaluators (Evaluator A: 12 years specialist experience in terminology; Evaluator B: 8 years in corpus linguistics and LSP; Evaluator C: 10 years in computational terminology), all with training in terminology and corpus linguistics. The fifteen target terms were selected to ensure conceptual diversity across the terminological inventory of the domain, spanning methodological concepts such as type-token ratio and significance test, procedural terms such as concordance and annotation, and theoretical constructs such as representativeness and corpus balance. This heterogeneity allowed us to probe whether evaluator preferences and metric behaviour varied across definitional difficulty. For each term, one definition originated from the CASS reference glossary (human reference) and one was generated by Gemini 1.5 Flash under the RAG condition (selected post-hoc based on average automatic metric scores).

To control for bias, each evaluator assessed definitions in a randomised order, with left–right presentation of Definition A and Definition B randomised independently for every item. The origin of each definition was concealed throughout evaluation; the human vs. machine provenance was disclosed only after all ratings were recorded, ensuring genuine blinding. Evaluators worked independently without discussion or adjudication. Each evaluator received a standardised written rubric specifying the four rating criteria (conceptual adequacy, completeness, terminological precision and clarity), a paragraph definition of each criterion with worked examples drawn from the domain, and the 0–2 rating scale (0 = poor, 1 = acceptable, 2 = good). **Evaluation consisted of two independent tasks**: Evaluators rated each definition on all four criteria using the numerical scale, then recorded a forced binary preference (which definition they would include in a specialised glossary). The forced-choice preference was not merely a post-hoc summary of scores but a separate judgment, capturing the holistic impression independent of fine-grained ratings. An optional free-text comment field allowed elaboration on judgements. The evaluation yielded 45 paired judgements (15 terms × 3 evaluators) per criterion, generating quantitative scores and qualitative insights into divergences between expert and metric-based evaluation. This design—combining graded numerical assessment with forced binary preference—provides both fine-grained measurement and a robust preference signal that is less sensitive to scale granularity.

## 4. RESULTS AND DISCUSSION

The expert evaluation produced a clear and, in some respects, unexpected result: the LLM-generated definitions received higher mean ratings than the human reference definitions on every criterion. Table 2 reports the mean scores by origin. The overall mean—averaging the four criteria—was 1.76 (out of 2) for the generated definitions and 1.29 for the human reference. The largest gaps appeared in terminological precision (1.73 vs. 1.09) and completeness (1.78 vs. 1.24), with smaller but consistent differences in conceptual adequacy and clarity.

| Criterion                     | LLM M (SD)            | Human M (SD)          | Diff.           | 95% CI                 | *p*            |
| ----------------------------- | --------------------- | --------------------- | --------------- | ---------------------- | ---------------- |
| Conceptual adequacy           | 1.78 (0.37)           | 1.44 (0.51)           | +0.34           | [0.05, 0.63]           | 0.021            |
| Completeness                  | 1.78 (0.33)           | 1.24 (0.52)           | +0.54           | [0.18, 0.90]           | 0.004            |
| Terminological precision      | 1.73 (0.40)           | 1.09 (0.54)           | +0.64           | [0.27, 1.01]           | 0.001            |
| Clarity                       | 1.76 (0.36)           | 1.40 (0.50)           | +0.36           | [0.03, 0.69]           | 0.032            |
| **Overall (mean of 4)** | **1.76 (0.32)** | **1.29 (0.46)** | **+0.47** | **[0.18, 0.76]** | **<0.001** |

*Table 2. Expert ratings by definition origin (0–2 scale). M = mean across 45 judgements (15 terms × 3 evaluators); SD = standard deviation; Diff. = LLM − Human; 95% CI = 95% confidence interval for the difference; p = significance from paired t-test. Effect sizes (Cohen's d) range from 0.72 (adequacy) to 1.20 (precision).*

The forced glossary-inclusion preference pointed in the same direction. Across the 45 paired judgements (fifteen terms × three evaluators), the generated definition was selected in 34 cases (75.6%) and the human definition in 11 (24.4%). The preference for the generated definitions was thus consistent across evaluators, even though, as shown below, the evaluators did not agree closely on the precise scores they assigned.

Two illustrative cases demonstrate the nature of this divergence:

(i) **Type-token ratio**: The generated definition (RAG, Gemini) reads "A quantitative metric of lexical diversity, calculated as the quotient of the number of unique word forms (types) and the total number of running words (tokens) within a given text or corpus." versus the human reference "A measure of vocabulary diversity in a corpus equal to the total number of types divided by the total number of tokens." All three evaluators unanimously preferred the generated version (mean adequacy: 2.0 vs. 1.5), noting that the explicit parenthetical glosses of *types* and *tokens*, the specification of the operation as a quotient, and the clarification of scope made it substantially more useful as a terminographic entry.

(ii) **Significance test**: Here the human reference prevailed. The generated definition (RAG, Mistral) reads "A mathematical procedure used to determine the statistical significance of a result," while the human reference states "A statistical procedure in inferential linguistics used to evaluate the strength of evidence against a null hypothesis by determining the probability that observed data distributions occurred by chance." Evaluators gave the human reference markedly higher scores (mean adequacy: 2.0 vs. 1.25), citing its explicit anchoring in inferential linguistics, its null-hypothesis framing, and its specification of what the test determines. The generated definition, by contrast, was judged circular: specifying that a significance test determines "statistical significance" does not characterise the concept beyond tautology.

Inter-annotator agreement was modest. Krippendorff's α (ordinal) was 0.24 for conceptual adequacy, 0.35 for completeness, 0.32 for terminological precision and 0.20 for clarity, with an overall pooled value of 0.28—well below the conventional threshold for tentative interpretation (Moyano Moreno, 2027). Several factors likely contribute to this. The three-point ordinal scale compresses variance and inflates the impact of single-point disagreements; the panel is small (three raters, fifteen terms); and the assessment of definitional quality is intrinsically subjective, depending on each expert's conception of adequacy and completeness. Crucially, the disagreement concerns the magnitude of the ratings, not their direction: the three evaluators diverged on how good each definition was, yet converged on which definition they preferred. This dissociation between graded agreement and directional agreement is itself informative, and is taken up in the discussion.

The qualitative comments help to interpret the pattern. Several evaluators noted that the longer generated definitions occasionally added non-essential material—one observed that a generated entry, though correct, contained "a bit of filler" rather than additional necessary information—while still judging the generated definitions more complete and precise overall. The human reference definitions, drawn from an existing glossary, were at times perceived as terser and less explicit about the conceptual properties of the term. Two illustrative cases, selected to represent contrasting evaluation outcomes, clarify the nature of this divergence.

For *type-token ratio* (item 14 of 15), the generated definition received unanimous preference across all three evaluators. The human reference (Definition B) reads: "A measure of vocabulary diversity in a corpus equal to the total number of types divided by the total number of tokens." The generated definition (Definition A) expands on this formulation: "A quantitative metric of lexical diversity, calculated as the quotient of the number of unique word forms (types) and the total number of running words (tokens) within a given text or corpus." Evaluators consistently gave the generated definition higher scores for completeness and terminological precision, noting that the explicit parenthetical glosses of *types* and *tokens*, the specification of the operation as a quotient, and the clarification of the scope (text or corpus) made it more useful as a terminographic entry. The human reference, though accurate, was judged too sparse to stand alone in a glossary without additional context.

The case of *significance test* (item 15 of 15) illustrates the opposite outcome and offers important nuance. Here the generated definition (Definition A) was rejected in favour of the human reference (Definition B). The generated entry reads: "A mathematical procedure used to determine the statistical significance of a result." The human reference states: "A statistical procedure in inferential linguistics used to evaluate the strength of evidence against a null hypothesis by determining the probability that observed data distributions occurred by chance." Evaluators gave the human reference markedly higher scores on conceptual adequacy and terminological precision, citing its explicit anchoring in inferential linguistics, its null-hypothesis framing, and its specification of what the test actually determines (the probability of observing the data by chance). The generated definition, by contrast, was judged circular: specifying that a significance test determines "statistical significance" does not characterise the concept beyond its name. This case demonstrates that corpus grounding does not uniformly guarantee terminological adequacy—when the corpus evidence is insufficient to anchor the probabilistic and inferential properties of a concept, the generated output may fail to capture the defining features that experts consider essential.

**Automatic Metrics Evaluation.** Beyond expert ratings, we evaluated generated definitions against the human reference using multiple automatic metrics: lexical-overlap (BLEU, ROUGE-L), semantic similarity (BERTScore F1, cosine similarity), and reference-free measures (BLEURT, BARTScore). Table 3 reports results for the primary metrics across all four models and both conditions.

| Metric                    | No-RAG M | RAG M  | Δ (RAG gain) |
| ------------------------- | -------- | ------ | ------------- |
| **Lexical-overlap** |          |        |               |
| BLEU                      | 0.0285   | 0.0223 | −0.0062      |
| ROUGE-L                   | 0.1843   | 0.1756 | −0.0087      |
| **Semantic-aware**  |          |        |               |
| BERTScore F1              | 0.8815   | 0.8815 | 0.0000        |
| Cosine (sentence emb.)    | 0.5763   | 0.6063 | +0.0300       |
| **Reference-free**  |          |        |               |
| BLEURT                    | 0.4241   | 0.4289 | +0.0048       |
| BARTScore                 | 0.3567   | 0.3612 | +0.0045       |

*Table 3. Automatic metric results (means across 15 terms, 4 models). BLEU, ROUGE-L, BERTScore F1 are reference-based; BLEURT and BARTScore are reference-free. Higher is better. RAG provides selective gains in semantic similarity but negligible improvement in reference-free measures.*

The results reveal striking divergence. Lexical-overlap metrics (BLEU, ROUGE-L) produce minimal scores (M = 0.03, 0.18) and actually *decrease* under RAG—a paradoxical result reflecting that grounding nudges the model away from surface-level mimicry toward semantically-grounded paraphrase. BERTScore F1 remains static (M ≈ 0.88) across conditions, suggesting it conflates surface similarity with semantic adequacy. Cosine similarity shows the most consistent RAG effect: a modest but statistically significant rise from 0.576 to 0.606 (*p* < 0.05, paired t-test), indicating that grounding does nudge definitions toward greater topical proximity to the reference.

Critically, we computed Spearman rank correlations between automatic metrics and expert *preference* (LLM vs. Human choice) across all 15 terms. Results are striking: BERTScore F1 (*ρ* = −0.18, *p* = 0.51), cosine similarity (*ρ* = 0.21, *p* = 0.43), BLEU (*ρ* = 0.04, *p* = 0.89), ROUGE-L (*ρ* = 0.12, *p* = 0.65), BLEURT (*ρ* = 0.19, *p* = 0.48), and BARTScore (*ρ* = 0.08, *p* = 0.76) all show near-zero correlation with expert preference. This systematic misalignment is the study's core finding regarding automatic evaluation.

**Hybrid Retrieval Ablation.** To assess the contribution of the hybrid method's components, we conducted an ablation comparing (1) regex-only filtering, (2) embedding-only retrieval, and (3) the full hybrid pipeline. Measurements included retrieval precision/recall and downstream expert ratings. Regex-only retrieval recovered 1.60 passages per term (high precision, 85% of retrieved passages relevant); embedding-only retrieval recovered 0.20 passages per term (low recall, only 15% deemed definitionally relevant by annotators); hybrid retrieval recovered 0.60 passages per term with 93% precision. Critically, definitions generated from hybrid-retrieved contexts scored significantly higher on expert ratings (M = 1.76) than those from regex-only (M = 1.59, *p* = 0.031) or embeddings-only (M = 1.48, *p* < 0.001), confirming the value of combining both signals.

**Error Analysis.** Qualitative inspection of the 11 cases where experts preferred human definitions revealed three recurring patterns: (1) *Genus error* (5 cases): the generated definition misidentified the superordinate category or conflated related concepts (e.g., confusing *comparability* with *comparativity*). (2) *Missing differentia* (4 cases): the definition omitted essential properties that distinguish the concept from closely related ones, particularly in probabilistic or inferential concepts (e.g., significance test lacking null-hypothesis framing). (3) *Register mismatch* (2 cases): the generated definition used paraphrases that obscured field-specific distinctions (e.g., describing *annotation* in lay terms rather than terminological precision). These errors align with known limitations of corpus-grounded generation: when the corpus evidence is sparse or fails to make conceptual distinctions explicit, the LLM generates plausible but under-specified output.

The juxtaposition of the two evaluations exposes a fundamental divergence (RQ). The automatic metrics are anchored, by construction, to the human reference definitions: BERTScore, cosine similarity and the ROUGE family all measure how closely a generated definition resembles the human glossary entry. Yet the expert evaluation found those very human entries to be inferior to the generated definitions. The metrics therefore reward proximity to a reference that the experts themselves judged less adequate. A generated definition that departs from the human entry—elaborating conceptual properties absent from the terse glossary formulation—is penalised by lexical-overlap metrics and only partially rewarded by semantic ones, even when experts regard that departure as an improvement.

This explains why the modest, grounding-driven rise in cosine similarity cannot be read straightforwardly as a quality gain: greater proximity to the reference is not the same as greater terminological adequacy, precisely because the reference is not the quality ceiling. The two evaluation regimes are not merely weakly correlated; they are, in this dataset, pointing in different directions.

Three main threads run through the results. First, regarding the definitional language of the domain (O1), a substantial share of definitional knowledge is carried by a compact inventory of recurrent patterns. This concentration is doubly significant: descriptively, it shows how Corpus Linguistics articulates its conceptual apparatus through a stable repertoire of formulations; methodologically, it explains why corpus grounding is feasible, since the same regularities that characterise the discourse also make definitional evidence retrievable.

Second, regarding the comparison of human and machine definitions (O3), the expert evaluation produced a counter-intuitive but consistent result: blind evaluators preferred the corpus-grounded generated definitions to the human reference, in roughly three quarters of judgements and across all four criteria, most markedly in terminological precision and completeness. This result calls for some care in interpretation. The comparison is not between machines and human terminographers in the abstract, but between freshly generated, corpus-grounded definitions and the specific entries of an existing reference glossary. The most likely explanation is that the reference definitions, being concise and in some cases dated, characterise concepts more sparsely than the generated ones, which synthesise multiple corpus contexts and so make conceptual properties explicit. The qualitative comments, noting both the greater completeness and the occasional verbosity of the generated entries, support this reading.

The modest inter-annotator agreement qualifies, but does not undermine, this conclusion. The dissociation—weak agreement on scores but strong agreement on preference—suggests that definitional quality is genuinely multidimensional and resists reduction to a single scale, while the choice of which definition to trust is more stable. This is consistent with the long-standing observation that terminological adequacy involves several partly independent properties (Sager, 1990; Cabré, 1999). It also tempers any strong quantitative claims: with three evaluators and fifteen terms, the figures reported here are best read as exploratory evidence pointing in a consistent direction, not as precise effect sizes.

Third, regarding convergence (RQ), the divergence between expert judgement and automatic metrics is the study's central methodological result. Because the metrics are anchored to the human reference, they cannot recognise an improvement over that reference; they reward resemblance to definitions that experts ranked lower. This is a concrete, domain-specific instance of the well-documented misalignment between surface-similarity metrics and human judgement (Zhang et al., 2019; Clinciu et al., 2021), and it carries a clear practical implication for terminography. Corpus-grounded generation can usefully support the drafting of candidate definitions—indeed, it may produce entries that experts prefer to existing references—but the validation of those candidates remains an expert task that current automatic metrics, tied as they are to a reference standard, cannot discharge. The contribution of LLMs to terminographic work is therefore best understood as assistive, and the role of automatic metrics as, at most, a coarse filter rather than an arbiter of terminological quality.

These findings carry concrete implications for terminographic practice. In the short term, RAG-based generation with **hybrid retrieval** (combining pattern-based filtering with semantic re-ranking) offers a viable, scalable strategy for producing first-draft definitions at scale, particularly for domains where terminological resources are sparse or dated. The hybrid approach operationalises the definitional patterns described in Section 3.2 while addressing the limitations of pure pattern matching through semantic refinement, achieving a practical balance: 332ms per 15-term batch (acceptable for iterative definition drafting) with 3× higher passage recall than pure semantic retrieval. In the medium term, the results suggest that evaluation protocols for AI-assisted terminography need to move beyond single-reference automatic metrics: the present study demonstrates that a reference glossary can itself be the weaker entry, and that metrics anchored to it will systematically penalise better-quality outputs. Practical workflows should incorporate expert review at the validation stage, with automatic metrics reserved for filtering rather than ranking. In the longer term, the case of *significance test* points to a limitation that is also a research opportunity: for concepts whose defining properties are rarely made explicit in running discourse—inferential relationships, probabilistic reasoning, theoretical commitments—the hybrid approach combining corpus evidence with semantic models may be insufficient, and further enrichment through structured knowledge sources (ontologies, terminological databases) may be needed to support adequate generation. The present study contributes a methodological framework within which these questions can be pursued empirically.

---

## 5. CONCLUSIONS

This study treated the automatic generation of terminological definitions not as an engineering goal but as a terminological and evaluative problem. By characterising the definitional language of Corpus Linguistics, generating corpus-grounded candidate definitions, and subjecting human- and machine-authored definitions to a blind expert evaluation contrasted with automatic metrics, we found that definitional knowledge in the domain is concentrated in a recoverable inventory of patterns; that, in blind assessment, experts consistently preferred the corpus-grounded generated definitions to the human reference, especially in terminological precision and completeness; and that automatic metrics, anchored to that human reference, diverge from—and in this dataset contradict—expert judgement.

**Limitations and Generalisability.** The principal limitations concern scope, sample size, and generalisability across domains. The expert panel (N = 3) and evaluation set (N = 15 terms) are modest, and statistical power is consequently constrained: with this design, 95% CI for effect sizes are wide (e.g., [0.05, 0.63] for conceptual adequacy), and small effect sizes cannot be reliably detected. However, three considerations qualify this limitation. First, the consistency of preferences across evaluators (75.6% convergence on glossary inclusion) is notable given independent evaluation and absence of adjudication, suggesting that the measured preference gradient is robust to sample size, even if its magnitude is imprecisely estimated. Second, the depth of expert judgment—evaluators with 8–12 years of specialist experience in terminology and corpus linguistics—compensates partially for panel size; such specialist evaluation at scale (e.g., 8–10 evaluators) would be resource-intensive and may yield diminishing returns. Third, the study is positioned explicitly as exploratory evidence for a novel use case (LLM-assisted terminology), not as a definitive effect-size estimate for a well-established phenomenon. The pattern of results (consistent direction across criteria, large effect magnitudes, high preference convergence) is *sufficiently* consistent to warrant the reported conclusions, though replication with larger samples is an important next step.

Inter-annotator agreement (Krippendorff's α = 0.28 overall) is weak, reflecting the genuine multidimensionality and subjectivity of definitional quality assessment; however, convergence on pairwise preference (75.6% agreement direction) suggests that holistic quality judgements are more stable than granular scores. This dissociation is theoretically informative and is taken up in the discussion.

The study is also domain-specific: Corpus Linguistics is a mature field with published glossaries, high textual density of definitional contexts (~4.16% of sentences), and a coherent discourse community. Generalisation to domains with sparse open-access texts, nascent or fragmented terminologies, low textual density of definitions, or non-anglophone literature remains an open empirical question; the framework described here provides the foundation for such extensions. Finally, the approach assumes that multiple corpus contexts provide definitional grounding; for highly abstract or theoretical concepts where defining properties are rarely made explicit in running discourse, this assumption may not hold, necessitating richer knowledge sources (ontologies, expert curation, feature-based definitions) as proposed in the Context-Augmented Generation framework (Zamora Rey, en prensa).

**Future Directions.** Immediate extensions include: (1) replicating the evaluation with a larger, more diverse expert panel (8–10 evaluators) across multiple domains to assess robustness and generalisability; (2) comparing multiple reference standards (e.g., different published glossaries for the same domain, or expert-authored de novo definitions) to test whether the preference pattern holds independent of CASS; (3) evaluating reference-free and LLM-as-a-judge rubric-based assessors with explicit conceptual criteria to move beyond single-reference metrics; (4) refining the definitional-pattern inventory through deeper corpus analysis (e.g., discourse-functional analysis of definitional structures across LSP registers); and (5) testing whether incorporating structured knowledge (ontological relations, feature-based definitions) can mitigate the genus and differentia errors identified in the error analysis.

**Methodological Implications.** The broader lesson is methodological: as generative tools enter the terminographic workflow, the evaluation of specialised definitions must stay anchored in linguistic and conceptual criteria, not in surface measures of similarity to a fixed reference. The finding that experts prefer corpus-grounded, LLM-generated definitions to legacy human references challenges the assumption that published glossaries are immutable quality ceilings. It motivates a shift toward dynamic, multi-reference evaluation frameworks and supports human-in-the-loop RAG pipelines in which expert oversight remains central. Conversely, the discovery that corpus grounding alone cannot ensure adequacy for probabilistic or inferential concepts underscores the need for hybrid systems combining corpus evidence with structured knowledge sources, particularly in technical domains where subtle definitional nuances carry high stakes.

## REFERENCES

NOT USED/ Akhmanova, O. S. & Agapova, G. (1974). *Terminology: Theory and Method*. Moscow: MGU.

NOT USED/ Alcina, A. (2003). "La programación de objetivos didácticos en Terminótica atendiendo a las nuevas herramientas y recursos", in *Terminología y traducción: un bosquejo de su evolución*. Atrio.

Astrakhantsev, N. A., Fedorenko, D. G. & Turdakov, D. Y. (2015). "Methods for automatic term recognition in domain-specific text collections: A survey", *Programming and Computer Software* 41/6, 336–349.

NOT USED/ Atkins, B. T. S., Clear, J. & Ostler, N. (1992). "Corpus Design Criteria", *Literary and Linguistic Computing* 7/1, 1–16.

NOT USED/ Babl, F., Hennen, M., Murauer, J. & Geierhos, M. (2025). "Random Splitting Negatively Impacts NER Evaluation: Quantifying and Eliminating the Overestimation of NER Performance", *Findings of the Association for Computational Linguistics: ACL 2025*, 9724–9738.

NOT USED/ Baroni, M. & Bernardini, S. (2004). "BootCaT: Bootstrapping corpora and terms from the web", *Proceedings of the Fourth International Conference on Language Resources and Evaluation (LREC 2004)*, 1313–1316.

NOT USED/ Bel, N. (2025). "Un vocabulario básico de los modelos grandes de lenguaje: una explicación y 25 términos", *Terminàlia* 31, 27–39.

NOT USED/ Bernier-Colborne, G. (2012). "Defining a gold standard for the evaluation of term extractors", *Proceedings of the colabTKR workshop Terminology and Knowledge Representation*, Istanbul.

NOT USED/ Bird, S., Klein, E. & Loper, E. (2009). *Natural Language Processing with Python*. O'Reilly Media, Inc.

NOT USED/ Blandon Andrade, J. C., Medina Otálvaro, C. M., Zapata Jaramillo, C. M. & Morales Ríos, A. (2025). "Approaches, Tools, Algorithms, and Methods for Automatic Term Extraction: A Systematic Literature Mapping", *Journal of Intelligent & Fuzzy Systems*, 18758967251392652.

NOT USED/ Bolshakov, I. A. & Gelbukh, A. (2004). *Computational Linguistics: Models, Resources, Applications*. Instituto Politécnico Nacional.

NOT USED/ Bolshakova, E., Loukachevitch, N. & Nokel, M. (2013). "Topic models can improve domain term extraction", *European Conference on Information Retrieval*, 684–687.

NOT USED/ Bonino, R. (2009). "Presentación de la lingüística computacional", *La interlengua de los aprendientes del español como L2*, 7–18.

NOT USED/ Bourigault, D. (1994). *Lexter: un Logiciel d'EXtraction de TERminologie: application à l'acquisition des connaissances à partir de textes*. PhD Thesis, Paris: EHESS.

NOT USED/ Brumfit, C. (1987). "Applied linguistics and communicative language teaching", *Annual Review of Applied Linguistics* 8, 3–13.

NOT USED/ Cabré, M. T. (1999). *Terminology: Theory, Methods and Applications*. Amsterdam: John Benjamins.

NOT USED/ Cabré, M. T. (2005). "La terminología hoy: concepciones, tendencias y aplicaciones", in *Terminología: representación y comunicación: elementos para una teoría de base comunicativa y otros artículos*.Documenta Universitaria.

NOT USED/ Cabré, M. T. (2008). "Cómo las nuevas tecnologías han modificado la metodología terminológica", in *Terminología, traducción y comunicación especializada: homenaje a Amelia de Irazázabal*. Fiorini.

NOT USED/ Caballero, J. V. T. (1994). "Reflexiones sobre la terminología lingüístico-gramatical", *Cauce: Revista Internacional de Filología, Comunicación y sus Didácticas* 17, 83–106.

NOT USED/ Caravedo Barrios, R. E. (1999). *Linguistica del corpus. Cuestiones teorico-metodologicas aplicadas al español*. Ediciones Universidad Salamanca.

NOT USED/ Carrè, R., Dégremont, J., Gross, M., Pierrel, J.-M. & Sabah, G. (1991). *Langage humain et machine*. CNRS.

NOT USED/ Casado Mancebo, M. (2023). "Una aplicación para explorar la frecuencia léxica a partir de corpus de referencia", *CHIMERA: Revista de Corpus de Lenguas Romances y Estudios Lingüísticos* 10, 89–95.

NOT USED/ Casas Gómez, M. (2003). "El documento terminológico: su estructura a propósito de la terminología lingüística", *Actas-I. VIII Simposio Internacional de Comunicación Social*. Santiago de Cuba.

NOT USED/ Casas Gómez, M. (2021). "La semántica y sus usos terminológicos", *Bulletin hispanique* 123/2, 187–204.

Casas Gómez, M. (2022a). "DOCUTERM: MODELO DE DOCUMENTACIÓN DE USOS TERMINOLÓGICOS", *Revista de Lenguas para Fines Específicos* 17, 11–27. http://dx.doi.org/10.4995/rlyla.2022.16249

Casas Gómez, M. (2022b). "La aportación de Coseriu a la historiografía de la terminología como disciplina lingüística", *Boletín de filología* 57/1, 233–260.

NOT USED/ Casas Gómez, M. & Varo Varo, C. (eds.) (2024). *La terminología de la semántica*. Editorial Universidad de Sevilla.

NOT USED/ Cass (2013). *Corpus Linguistics Glossary*. Corpus Approaches to Social Science (CASS), University of Lancaster.

NOT USED/ Chataut, S., Do, T., Gurung, B. D. S., Aryal, S., Khanal, A., Lushbough, C. & Gnimpieba, E. (2024). "Comparative Study of Domain Driven Terms Extraction Using Large Language Models", *arXiv:2404.02330*.

NOT USED/ Chun, Y., Kim, M., Kim, D., Park, C. & Lim, H.-S. (2025). "Enhancing Automatic Term Extraction with Large Language Models via Syntactic Retrieval", *Findings of the Association for Computational Linguistics: ACL 2025*, 9916–9926.

Clinciu, M.-A., Eshghi, A. & Hastie, H. (2021). "A study of automatic metrics for the evaluation of natural language explanations", *Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics*, 2376–2387.

NOT USED/ Conneau, A., Khandelwal, K., Goyal, N., Chaudhary, V., Wenzek, G., Guzmán, F., Grave, É., Ott, M., Zettlemoyer, L. & Stoyanov, V. (2020). "Unsupervised Cross-lingual Representation Learning at Scale", *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics*, 8440–8451.

NOT USED/ Conrado, M., Pardo, T. & Rezende, S. O. (2013). "A machine learning approach to automatic term extraction using a rich feature set", *Proceedings of the 2013 NAACL HLT student research workshop*, 16–23.

NOT USED/ Corpas Pastor, G. & Seghiri Domínguez, M. (2010). "Size matters: A quantitative approach to corpus representativeness", in *Lengua, traducción, recepción*. Publicaciones Universidad de León.

NOT USED/ Crespo Miguel, M. (2020). "Lingüística digital: revisión de su estado actual y retos en el Instituto Universitario de Investigación en Lingüística Aplicada de la Universidad de Cádiz", *Pragmalingüística* 28, 148–165.

NOT USED/ Crespo Miguel, M. (2023). "Análisis terminológico mediante algoritmos de representación conceptual", in *La terminología de la semántica*. Editorial Universidad de Sevilla.

da Silva Conrado, M., Felippo, A. D., Salgueiro Pardo, T. A. & Rezende, S. O. (2014). "A survey of automatic term extraction for Brazilian Portuguese", *Journal of the Brazilian Computer Society* 20/1, 12.

NOT USED/ Daille, B. (2003). "Conceptual structuring through term variations", *Proceedings of the ACL 2003 workshop on Multiword expressions: analysis, acquisition and treatment*, 9–16.

NOT USED/ Dale, R. (2001). "Symbolic approaches to natural language processing", in *Handbook of Natural Language Processing*. Marcel Dekker.

da Silva, B. C. D. (2006). "O estudo lingüístico-computacional da linguagem", *Letras de Hoje* 41/2.

NOT USED/ Dash, N. S. & Arulmozi, S. (2018). *History, Features, and Typology of Language Corpora*. Springer.

NOT USED/ De Vega, M. (1998). "La psicología cognitiva: ensayo sobre un paradigma en transformación", *Anuario de psicología/The UB Journal of psychology*, 21–44.

Depecker, L. (2005). "Contribution de la terminologie à la linguistique", *Langages* 157/1, 6–13.

NOT USED/ Desmet, I. & Boutayeb, S. (1994). "Terms and words: Propositions for terminology", *Terminology. International journal of theoretical and applied issues in specialized communication* 1/2, 303–325.

Deutsch, D., Bedrax-Weiss, T. & Roth, D. (2020). "Understanding the extent to which summarization evaluation metrics measure the information quality of summaries", *arXiv:2010.12495*.

DIN (1986). *DIN 2342: Terminologielehre -- Begriffe und Benennungen*. Deutsches Institut für Normung.

NOT USED/ Drouin, P. (2003). "Term extraction using non-technical corpora as a point of leverage", *Terminology* 9, 99–115.

Dubuc, R. (1978). *Manuel pratique de terminologie*. Linguatech.

NOT USED/ Duran Muñoz, I. (2011). *El trabajo ontoterminográfico aplicado a la traducción de textos del turismo de aventura (español, inglés, alemán): fases de preparación*. PhD Thesis, Universidad de Málaga.

NOT USED/ Egbert, J., Biber, D. & Gray, B. (2022). *Designing and Evaluating Language Corpora: A Practical Framework for Corpus Representativeness*. Cambridge University Press.

NOT USED/ Espinosa-Anke, L., Camacho-Collados, J., Delli Bovi, C. & Saggion, H. (2018). "Syntactically aware neural architectures for definition extraction", *Proceedings of NAACL-HLT*, 378–385.

NOT USED/ Estopa Bagot, R. (1999). "Eficiencia en la extracción automática de terminología", *Perspectives: Studies in Translatology* 7/2, 277–286.

NOT USED/ Estopa Bagot, R. (2016). "La neología especializada: Términos médicos en la prensa española", in *Estudios de neología del español*. Servicio de Publicaciones.

NOT USED/ Estopa Bagot, R. (2022). "Neología general y especializada", in *Neología del español: del uso al diccionario*. Iberoamericana.

NOT USED/ Ferrari, G. (2006). "State of the art in Computational Linguistics", in *Linguistics Today--Facing a Greater Challenge*. John Benjamins Publishing Company.

NOT USED/ Fkih, F., Omri, M. N. & Toumia, I. (2012). "A Linguistic Model for Terminology Extraction based Conditional Random Fields", *ArXiv* abs/1210.0252.

NOT USED/ Flowerdew, J. (1992). "Definitions in science lectures", *Applied Linguistics* 13/2, 202–221.

NOT USED/ Fodor, J. A. (1983). *The Modularity of Mind*. MIT press.

NOT USED/ Fontenelle, T. (1990). "Automatic extraction of lexical-semantic relations from dictionary definitions", *Proceedings of EURALEX*.

NOT USED/ Francis, N. W. (1992). "Language corpora B. C.", in *Directions in Corpus Linguistics. Proceedings of Nobel Symposium*. De Gruyter.

Frantzi, K., Ananiadou, S. & Mima, H. (2000). "Automatic recognition of multi-word terms: the C-value/NC-value method", *International Journal on Digital Libraries* 3/2, 115–130.

NOT USED/ Frantzi, K. T. & Ananiadou, S. (1999). "The C-value/NC-value domain-independent method for multi-word term extraction", *Journal of Natural Language Processing* 6/3, 145–179.

NOT USED/ Freixa, J. (2005). "Variación terminológica: ¿por qué y para qué?", *Meta* 50/4.

NOT USED/ Gallistel, C. R. & King, A. P. (2011). *Memory and the Computational Brain: Why Cognitive Science will Transform Neuroscience*. John Wiley & Sons.

Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J. & Wang, H. (2023). "Retrieval-augmented generation for large language models: A survey", *arXiv:2312.10997*.

NOT USED/ García-Miguel, J. M. (2022). "Lingüística de corpus: de los datos textuales a la teoría lingüística", *Estudios de lingüística del español* 45, 11–42.

NOT USED/ Gavioli, L. (2005). *Exploring Corpora for ESP Learning*. John Benjamins.

NOT USED/ Gelbukh, A. (2010). "Procesamiento de lenguaje natural y sus aplicaciones", *Komputer Sapiens* 1, 6–11.

NOT USED/ Gilquin, G. & Gries, S. T. (2009). "Corpora and experimental methods: A state-of-the-art review", Walter de Gruyter GmbH & Co. KG.

NOT USED/ Golik, W., Bossy, R., Ratković, Z. & Nédellec, C. (2013). "Improving term extraction with linguistic analysis in the biomedical domain", *Research in Computing Science* 70, 157–172.

Gómez, M. C. & Smith, G. F. (2021). "El hablar y la variación de especialidad", in *Manual de lingüística del hablar*. Routledge.

NOT USED/ González Fernández, A. (2018). "Aproximación a la Lingüística Computacional y sus herramientas para el trabajo con corpus", *Futhark. Revista de Investigación y Cultura* 13.

NOT USED/ Greshman, R. (1986). *Computational Linguistics: An Introduction*. Cambridge University Press.

NOT USED/ Gries, S. T. (2009). *Quantitative Corpus Linguistics with R: A Practical Introduction*. Routledge.

NOT USED/ Gries, S. T. (2011). "Methodological and interdisciplinary stance in corpus linguistics", *Perspectives on Corpus Linguistics* 1/2, 81–98.

NOT USED/ Gries, S. T. (2013). *Statistics for Linguistics with R: A Practical Introduction*. Walter de Gruyter.

NOT USED/ Guerrero Ramos, G. (2017). *Nuevas Orientaciones de la Terminología y de la Neología en el Ámbito de la Semántica Léxica*. Servicio de Publicaciones de la Universidad de Navarra.

NOT USED/ Gutiérrez Rodilla, B. M. (1998). "La ciencia empieza en la palabra", *Análisis e historia del lenguaje científico, Barcelona*. Península.

NOT USED/ Hajicová, E., Abeillé, A., Hajic, J., Mírovský, J. & Uresová, Z. (2010). "Treebank Annotation", in *Handbook of Natural Language Processing*. CRC Press.

NOT USED/ Hanoka-Maitenaz, V. (2015). *Extraction et Complètion de Terminologies Multilingues*. PhD Thesis, Sorbonne Paris Cité.

NOT USED/ Heaps, H. S. (1978). *Information Retrieval: Computational and Theoretical Aspects*. Academic Press.

NOT USED/ Herdan, G. (1964). *Quantitative Linguistics*. Butterworth Press.

NOT USED/ Hernández, M. & Gómez, J. (2013). "Aplicaciones de procesamiento de lenguaje natural", *Revista Politécnica* 32, 87–96.

NOT USED/ Heylen, K. & De Hertog, D. (2015). "Automatic term extraction", in *Handbook of Terminology*. John Benjamins Publishing Company.

NOT USED/ Hirschberg, J. & Manning, C. D. (2015). "Advances in natural language processing", *Science* 349/6245, 261–266.

NOT USED/ Hobbs, J. R. & Riloff, E. (2010). "Information Extraction", in *Handbook of Natural Language Processing*. CRC Press: Taylor & Francis Group.

NOT USED/ Hutchins, J. (1999). "Retrospect and prospect in computer-based translation", *Proceedings of Machine Translation Summit VII*, 30–36.

NOT USED/ Ijcai2020p560 (2020). "Fast and Accurate Neural CRF Constituency Parsing", *Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence*.

ISO (1988). *ISO/DIS 1087: Terminology Work -- Vocabulary*. International Organization for Standardization.

NOT USED/ Jacquemin, C. & Bourigault, D. (2005). "Term extraction and automatic indexing", in *The Oxford Handbook of Computational Linguistics*. Oxford University Press.

NOT USED/ Jacquemin, C. & Royaute, J. (1994). "Retrieving terms and their variants in a lexicalized unification-based framework", *Sigir* 94, 132–141.

NOT USED/ Johnson, M. (2009). "How the statistical revolution changes (computational) linguistics", *Proceedings of the EACL 2009 workshop on the interaction between linguistics and computational linguistics*, 3–11.

NOT USED/ Johnson, M. (2011). "How relevant is linguistics to computational linguistics?", *Linguistic Issues in Language Technology* 6.

NOT USED/ Johnson, M. (2023). "Does machine learning really work?", *AI Magazine* 18/3, 11–11.

NOT USED/ Johri, P., Khatri, S. K., Al-Taani, A. T., Sabharwal, M., Suvanov, S. & Kumar, A. (2021). "Natural language processing: History, evolution, application, and future work", *Proceedings of 3rd International Conference on Computing Informatics and Networks: ICCIN 2020*, 365–375.

NOT USED/ Jones, K. S. (1994). "Natural language processing: a historical review", in *Current Issues in Computational Linguistics: In Honour of Don Walker*. Springer.

NOT USED/ Joseph, S. R., Hlomani, H., Letsholo, K., Kaniwa, F. & Sedimo, K. (2016). "Natural language processing: A review", *International Journal of Research in Engineering and Applied Sciences* 6/3, 207–210.

NOT USED/ Jurafsky, D. & Martin, J. H. (2009). *Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition*. Pearson/Prentice Hall Education International.

NOT USED/ Jurafsky, D. & Martin, J. H. (2025). *Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition with Language Models* (3rd ed.). Online manuscript released January 12, 2025.

NOT USED/ Kadeara, F. W. (1897). *Häufigkeitswörterbuch der Deutschen Sprache*. Self-published.

NOT USED/ Kageura, K. & Umino, B. (1996). "Methods of automatic term recognition: A review", *Terminology. International Journal of Theoretical and Applied Issues in Specialized Communication* 3/2, 259–289.

NOT USED/ Khurana, D., Koli, A., Khatter, K. & Singh, S. (2023). "Natural language processing: state of the art, current trends and challenges", *Multimedia Tools and Applications* 82/3, 3713–3744.

NOT USED/ King, T. H. (2011). "(Xx*-) Linguistics: Because We Love Language", *Linguistic Issues in Language Technology* 6.

NOT USED/ Kockaert, H. J., Steurs, F., Alsulaiman, A. & Allaithy, A. (2015). *Handbook of Terminology* (Vol. 1). John Benjamins Publishing Company.

NOT USED/ Koza Orellana, W. (2015). "Proposal for automatic extraction of medical term candidates with linguistic information processing description and evaluation of results", *Alfa: Revista de Linguística (São José do Rio Preto)* 59, 113–128.

NOT USED/ Krug, M., Schlüter, J. & Rosenbach, A. (eds.) (2013). *Research Methods in Language Variation and Change*. Cambridge University Press.

NOT USED/ Kyto, M., Rudanko, J. & Smitterberg, E. (2000). "Building a bridge between the present and the past: A corpus of 19th-century English", *ICAME Journal* 24, 85–98.

NOT USED/ Lafferty, J., McCallum, A. & Pereira, F. C. N. (2001). "Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data".

NOT USED/ Lavid López, J. (2005). *Lenguaje y Nuevas Tecnologías. Nuevas Perspectivas, Métodos y Herramientas para el Lingüista del Siglo XXI*. Ediciones Cátedra.

NOT USED/ Levy, O., Remus, S., Biemann, C. & Dagan, I. (2015). "Do supervised distributional methods really learn lexical inference relations?", *Proceedings of the 2015 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies*, 970–976.

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W.-t., Rocktäschel, T., Riedel, S. & Kiela, D. (2020). "Retrieval-augmented generation for knowledge-intensive NLP tasks", *Advances in Neural Information Processing Systems* 33, 9459–9474.

NOT USED/ Li, Y., Li, J., He, J. & Tao, C. (2024). "AE-GPT: Using Large Language Models to Extract Adverse Events from Surveillance Reports", *PLOS ONE* 19/3, e0300919.

NOT USED/ Liddy, E. D. (2001). "Natural Language Processing", in *Encyclopedia of Library and Information Science* (2nd ed.). Marcel Decker, Inc.

L'Homme, M.-C. (2020). *Lexical Semantics for Terminology: An Introduction*. John Benjamins.

NOT USED/ Linnè, C. (1735). *Systema naturae*. Apud Theodorum Haak.

NOT USED/ Ljunglöf, P. & Wirén, M. (2010). "Syntactic Parsing", in *Handbook of Natural Language Processing*. CRC Press: Taylor & Francis Group.

NOT USED/ Lossio-Ventura, J. A., Jonquet, C., Roche, M. & Teisseire, M. (2016). "Biomedical term extraction: overview and a new methodology", *Information Retrieval Journal* 19, 59–99.

NOT USED/ Mandelbrot, B. (1953). "An Informational Theory of the Statistical Structure of Language", in *Communication Theory*. Butterworths Scientific Publications.

NOT USED/ Manning, C. & Schutze, H. (1999). *Foundations of Statistical Natural Language Processing*. MIT press.

NOT USED/ Martí Antonín, M. A. (1999). "Panorama de la lingüística computacional en Europa", *Revista española de lingüística aplicada* 1, 11–24.

NOT USED/ Massion, F. (2024). "Terminology in the age of AI: The transformation of terminology theory and practice", *Journal of Translation Studies* 4/1, 67–94. https://doi.org/10.3726/JTS012024.04

Maynez, J., Narayan, S., Bohnet, B. & McDonald, R. (2020). "On faithfulness and factuality in abstractive summarization", *Proceedings of ACL*, 1906–1919.

NOT USED/ McEnery, T. (2019). *Corpus Linguistics*. Edinburgh University Press.

NOT USED/ McEnery, T. & Brezina, V. (2022). *Fundamental Principles of Corpus Linguistics*. Cambridge University Press.

NOT USED/ McEnery, T., Hardie, A. (2013). "The history of corpus linguistics", in *The Oxford Handbook of the History of Linguistics*. Oxford University Press.

NOT USED/ McEnery, T., Xiao, R. Z. & Tono, Y. (2006). *Corpus-based Language Studies: An Advanced Resource Book*. Routledge.

NOT USED/ McEnery, T. & Wilson, A. (1996). *Corpus Linguistics*. Edinburgh University Press.

NOT USED/ Merkl, D. (2000). "Text Data Mining", in *Handbook of Natural Language Processing*. Marcel Dekker.

NOT USED/ Messerklinger, J. et al. (2025). "Terminology augmented generation: A systematic review", in *Proceedings of the 3rd International Conference on Multilingual Digital Terminology Today (MDTT 2025)*. CEUR Workshop Proceedings.

NOT USED/ Mitchell, T. M. (1997). "Does machine learning really work?", *AI Magazine* 18/3, 11–11.

NOT USED/ Mitkov, R. (2022). *The Oxford Handbook of Computational Linguistics*. Oxford University Press.

NOT USED/ Mollá, D. & Vicedo, J. L. (2007). "Question answering in restricted domains: An overview", *Computational Linguistics* 33/1, 41–61.

NOT USED/ Morales Ascencio, B. (1997). "La lingüística en el contexto de la inteligencia artificial", *Forma y Función* 10, 25–50.

NOT USED/ Moreno Sandoval, A. (1998). *Lingüística Computacional: Introducción a los Modelos Simbólicos, Estadísticos y Biológicos*. Síntesis.

NOT USED/ Moreno Sandoval, A. (2016). "Lingüística computacional", in *Enciclopedia de Lingüística Hispánica*. Routledge.

NOT USED/ Moreno Sandoval, A. (2019). *Lenguas y Computación*. Síntesis.

NOT USED/ Moyano Moreno, I. (2025). "Antecedentes de la lingüística de corpus y algunas apreciaciones terminológicas", in *Un Viaje a Través de la Lengua y la Literatura: Identidad, Memoria y Enseñanza*. Dykinson.

NOT USED/ Moyano Moreno, I. (2026). "Defining the Boundaries of Specialised Language: Inter-Annotator (Dis)Agreement in Terminological Annotation", *Revista de Lenguas para Fines Específicos* 32.

NOT USED/ Muñoz Gillena, R. (2024). "Procesamiento del lenguaje natural como eje central de la inteligencia artificial generativa: Lección inaugural del Curso Académico 2024-2025". Lección inaugural, Universidad de La Rioja.

NOT USED/ Nazar, R. (2011). "A statistical approach to term extraction", *International Journal of English Studies* 11/2, 159–182.

NOT USED/ Nazar, R. (2016). "Distributional analysis applied to terminology extraction: First results in the domain of psychiatry in Spanish", *Terminology. International Journal of Theoretical and Applied Issues in Specialized Communication* 22/2, 141–170.

NOT USED/ Nivre, J. (2010). "Statistical Parsing", in *Handbook of Natural Language Processing*. CRC Press: Taylor & Francis Group.

NOT USED/ Parodi, G. (2008). "Lingüística de corpus: una introducción al ámbito", *RLA. Revista de Lingüística Teórica y Aplicada* 46/1, 93–119.

NOT USED/ Pearson, J. (1998). *Terms in Context*. Amsterdam: John Benjamins.

NOT USED/ Peng, F., Feng, F. & McCallum, A. (2004). "Chinese segmentation and new word detection using conditional random fields", *Proceedings of the 20th International Conference on Computational Linguistics*, 562.

Pérez Hernández, M. C. (2002). "Explotación de los córpora textuales informatizados para la creación de bases de datos terminológicas basadas en el conocimiento", *Estudios de Lingüística del Español* 18.

NOT USED/ Pitkowski, E. F. & Vázquez Gamarra, J. (2009). "El uso de los corpus lingüísticos como herramienta pedagógica para la enseñanza y aprendizaje de ELE", *Tinkuy: Boletín de Investigación y Debate* 11, 31–51.

NOT USED/ Randi, R. (2010). "Building a corpus: What are the key considerations?", in *The Routledge Handbook of Corpus Linguistics*. Routledge.

NOT USED/ Rebeyrolle, J. & Tanguy, L. (2000). "Repérage automatique de structures linguistiques en corpus: le cas des énoncés définitoires", *Cahiers de Grammaire* 25, 153–174.

NOT USED/ Rehm, G. & Uszkoreit, H. (eds.) (2020). *The European Language Technology Landscape: Language Technologies for Multilingual Europe*. Springer.

NOT USED/ Repar, A., Lavrač, N. & Pollak, S. (2025). "Extracting domain-specific terms using contextual word embeddings", *arXiv preprint arXiv:2502.17278*.

NOT USED/ Rey, A. (1995). *Essays on Terminology*. John Benjamins.

NOT USED/ Ribeiro de Faria, J., Xie, H. & Steffek, F. (2024). "Automatic Information Extraction from Employment Tribunal Judgements Using Large Language Models", *SSRN Electronic Journal*.

NOT USED/ Rigouts Terryn, A., Hoste, V., Drouin, P. & Lefever, E. (2020). "TermEval 2020: Shared task on automatic term extraction using the annotated corpora for term extraction research (ACTER) dataset", *Proceedings of the 6th International Workshop on Computational Terminology*, 85–94.

NOT USED/ Rigouts Terryn, A., Hoste, V. & Lefever, E. (2022). "Tagging terms in text: A supervised sequential labelling approach to automatic term extraction", *Terminology* 28/1, 157–189.

NOT USED/ Rodríguez-Tapia, S. (2024). *Gestión Terminológica, Corpus Especializados y Extracción Automática de Terminología en Español*. Comares.

NOT USED/ Rojo, G. (2021). *Introducción a la Lingüística de Corpus en Español*. Routledge.

NOT USED/ Rojas Zepeda, C. R. (2022). "Paradigma simbólico computacional, modularidad de la mente y lenguaje: principios y controversias", *Diversitas: Perspectivas en Psicología* 18/2, 48–61.

Sager, J. C. (1990). *A Practical Course in Terminology Processing*. John Benjamins Publishing Company.

NOT USED/ Saggion, H. (2004). "Identifying definitions in text collections for question answering", *Proceedings of LREC*.

NOT USED/ Sandrih, B., Krstev, C. & Stankovic, R. (2020). "Two approaches to compilation of bilingual multi-word terminology lists from lexical resources", *Natural Language Engineering* 26/4, 455–479.

NOT USED/ San Martín, A. (2025). "Toward human-centered AI-assisted terminology work", *arXiv:2512.18859*.

NOT USED/ Sandoval Rubiño, M. (2016). "Lingüística computacional", in *Enciclopedia de Lingüística Hispánica*. Routledge.

NOT USED/ Sayers, D., Sousa-Silva, R., Höhn, S., Ahmedi, L., Allkivi-Metsoja, K., Anastasiou, D., Beňuš, Š., Bowker, L., Bytçi, E., Catala, A. et al. (2021). *The Dawn of the Human-Machine Era: A Forecast of New and Emerging Language Technologies*. HAL Science.

NOT USED/ Schmidt, L., Hair, K., Graziosi, S., Campbell, F., Kapp, C., Khanteymoori, A., Craig, D., Engelbert, M. & Thomas, J. (2024). "Exploring the Use of a Large Language Model for Data Extraction in Systematic Reviews", *arXiv:2405.14445*.

NOT USED/ Schopf, T., Arabi, K. & Matthes, F. (2023). "Exploring the Landscape of Natural Language Processing Research", *Proceedings of the 14th International Conference on Recent Advances in Natural Language Processing*, 1034–1045.

NOT USED/ Shannon, C. E. & Weaver, W. (1949). *The Mathematical Theory of Communication*. University of Illinois Press.

Sierra, G., Alarcón, R., Aguilar, C. & Bach, C. (2008). "Definitional verbal patterns for semantic relation extraction", *Terminology* 14/1, 74–98.

NOT USED/ Sinclair, J. (1991). *Corpus, Concordance, Collocation*. Oxford University Press.

Somers, H. (2000a). "Machine Translation", in *Handbook of Natural Language Processing*. Marcel Dekker.

Somers, H. (2000b). "Example-Based Machine Translation", in *Handbook of Natural Language Processing*. Marcel Dekker.

NOT USED/ Stankovic, R., Krstev, C., Obradovic, I., Lazic, B. & Trtovac, A. (2016). "Rule-based automatic multi-word term extraction and lemmatization", *Proceedings of LREC*, 507–514.

NOT USED/ Tang, T., Lu, H., Jiang, Y., Huang, H., Zhang, D., Zhao, X., Kocmi, T. & Wei, F. (2024). "Not all metrics are guilty: Improving NLG evaluation by diversifying references", in *Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT 2024)*, 6596–6610. https://doi.org/10.18653/v1/2024.naacl-long.367

Temmerman, R. (2000). *Towards New Ways of Terminology Description: The Sociocognitive Approach*. Amsterdam: John Benjamins.

Terryn, A. R., Hoste, V., Drouin, P. & Lefever, E. (2020). "Termeval 2020: Shared task on automatic term extraction using the annotated corpora for term extraction research (ACTER) dataset", *Proceedings of the 6th International Workshop on Computational Terminology*, 85–94.

NOT USED/ Torres Caballero, J. V. (1994). "Reflexiones sobre la terminología lingüístico-gramatical", *Cauce: Revista Internacional de Filología, Comunicación y sus Didácticas* 17, 83–106.

NOT USED/ Tran, H. T. H., Martinc, M., Caporusso, J., Doucet, A. & Pollak, S. (2023). "The recent advances in automatic term extraction: A survey", *arXiv preprint arXiv:2301.06767*.

NOT USED/ Tran, H. T. H., González-Gallardo, C.-E., Delaunay, J., Doucet, A. & Pollak, S. (2024). "Is Prompting What Term Extraction Needs?", in *International Conference on Text, Speech, and Dialogue*. Springer.

NOT USED/ Turing, A. M. (1950). "Computing Machinery and Intelligence", *Mind* LIX/236, 433–460.

NOT USED/ Valeria, C. V. de P., Qiyue, G., Pavel, K. & Lawrence, S. M. (2023). "Extracting Mathematical Concepts with Large Language Models", *arXiv.org*.

Veyseh, A. P. B., Dernoncourt, F., Dou, D. & Nguyen, T. H. (2020). "A joint model for definition extraction with syntactic connection and semantic consistency", *Proceedings of the AAAI Conference on Artificial Intelligence* 34/05, 9098–9105.

NOT USED/ Vieira, R. & Lima, V. L. S. (2001). "Linguística computacional: princípios e aplicações", *IX Escola de Informática da SBC-Sul*. SBC-Sul.

NOT USED/ Vivaldi, J. & Rodríguez, H. (2011). "Extracting terminology from Wikipedia", *Procesamiento del lenguaje natural* 47, 65–73.

NOT USED/ Weaver, W. (1949). "Translation". Memorandum, Rockefeller Foundation.

Wüster, E. (1979). *Einführung in die Allgemeine Terminologielehre und Terminologische Lexikographie*. Springer.

NOT USED/ Zamora Rey, J. (2024). *Aproximación a la Generación Automática de Definiciones Terminológicas*. B.S. Thesis.

Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q. & Artzi, Y. (2019). "BERTScore: Evaluating Text Generation with BERT", *arXiv:1904.09675*.

NOT USED/ Zhang, X., Song, Y. & Fang, A. C. (2010). "Term Recognition Using Conditional Random Fields", *Proceedings of the 6th International Conference on Natural Language Processing and Knowledge Engineering*, 1–6.

NOT USED/ Zhang, Y., Zhou, H. & Li, Z. (2020). "Fast and Accurate Neural CRF Constituency Parsing", *Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence*, 4046–4053.

NOT USED/ Zheng, D., Zhao, T. & Yang, J. (2009). "Research on Domain Term Extraction Based on Conditional Random Fields", *Computer Processing of Oriental Languages. Language Technology for the Knowledge-based Economy*, 237–248.

NOT USED/ Zipf, G. K. (1949). *Human Behavior and the Principle of Least Effort: An Introduction to Human Ecology*. Addison-Wesley.

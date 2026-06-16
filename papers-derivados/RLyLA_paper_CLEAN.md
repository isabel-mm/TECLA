# CAN LARGE LANGUAGE MODELS WRITE TERMINOLOGICAL DEFINITIONS? EXPERT JUDGMENT VERSUS AUTOMATIC METRICS IN CORPUS LINGUISTICS

[AUTHOR(S)]
*[Affiliation]*

---

**Abstract**

Terminological definition constitutes a critical yet underexplored stage of terminographic work: unlike term extraction, it requires representing conceptual content with precision and domain adequacy. This study examines how automatically generated definitions compare to expert-authored ones in the domain of Corpus Linguistics, and whether expert judgement aligns with automatic evaluation metrics. We first characterise the definitional language of a specialised corpus of over one million words, identifying the lexico-syntactic patterns that convey definitional knowledge. Building on this evidence, we generate candidate definitions with large language models grounded in corpus-derived contexts. Definitions of human and machine origin were then assessed by three expert annotators in a blind, paired design across four criteria—conceptual adequacy, completeness, terminological precision and clarity—and benchmarked against lexical and semantic metrics. In a blind comparison, evaluators consistently preferred the corpus-grounded generated definitions over the human reference, revealing systematic divergences between expert judgement and automatic measures.

**Keywords:** terminology; terminological definition; corpus linguistics; large language models; evaluation; specialised lexicography.

---

## 1. INTRODUCTION

Terminology plays a central role in the organisation, representation and transmission of specialised knowledge (Cabré, 1999; Temmerman, 2000). The discipline emerged in the early twentieth century as a practical necessity (Dubuc, 1978), and has currently evolved from normative standardisation toward a more linguistically-grounded and corpus-based approach grounded in large-scale digital corpora (Sinclair, 1991; Francis, 1992). Terminological resources, such as glossaries, databases and/or ontologies, support specialised lexicography, knowledge management, and language technologies including information extraction, machine translation, question-answering systems, and semantic search (Kockaert & Steurs, 2015; Rodríguez-Tapia, 2024). Since the 1990s, terminographic work has been shaped by a growing collaboration between language technologies and expert validation, enabled by advances in Natural Language Processing (NLP) (Manning & Schutze, 1999; Jurafsky & Martin, 2009). Research efforts have concentrated heavily on Automatic Term Extraction (ATE), with substantial progress rangin from early pattern-based and statistical methods to the recent adoption of Machine Learning (ML) and neural approaches (Heylen & De Hertog, 2015; Lossio-Ventura et al., 2016). Yet terminological definition formulation remains largely manual. While identifying which lexical units are terms has seen its methodological advances, the task remains complex: term boundaries are often fuzzy, synonymy creates ambiguity, and the notion of what constitutes a "term" itself has been historically contested (Rey, 1995; Moyano Moreno, 2027). Characterizing what each term means is a fundamentally different, and even more complex challenge, since it requires capturing conceptual relations (Casas Gómez, 2020, 2022), establishing categories, and the profiling the distinctions that separate one concept from another (Cabré, 1999; Sager, 1990). This gap between automated extraction and manual definition-crafting has long constrained terminographic practice, leaving the latter as the labour-intensive frontier (Faber & L'Homme, 2022).

Recent advances in Large Language Models (LLMs) are reshaping terminographic practice in much the same way that computers transformed the field decades earlier (Costa, 2025). Just as the arrival of computational tools in the 1970s–1990s displaced manual extraction work, LLMs are now making automatic definition generation feasible at scale (Espinosa-Anke et al., 2018; Massion, 2024). However, although LLMs produce fluent, dictionary-like outputs with minimal prompting (Bel Rafecas, 2025), their outputs are known to suffer from factual inaccuracies and unsupported content (commonly called *hallucinations*) particularly in highly specialised domains (Maynez et al., 2020; Ji et al., 2023), meaning that, even though a definition may therefore be linguistically plausible, it might still fail to characterise the underlying concept. One promising approach is to ground generation in domain evidence through Retrieval Augmented Generation (RAG): supplying the model with corpus-derived contexts relevant to the target term, which should in principle reduce hallucinations and anchor definitions in attested usage. Importantly, RAG represents a convergence of two threads: LLM capability (the new technology) and corpus-based methodology (the established terminographic practice of the past three decades). Rather than abandoning the corpus-grounded approaches that have defined modern terminology work, RAG integrates LLM generation with the same evidence-based principle that has structured terminographic practice since the 1990s. Yet this raises a central evaluative question: if a machine can draft a definition quickly when grounded in corpus evidence, how do we determine whether it actually captures the concept correctly?

This study addresses that problem in the domain of Corpus Linguistics by directly comparing expert assessment with automatic evaluation. We examine how corpus-grounded LLM-generated definitions perform when evaluated by expert terminographers, and crucially, whether expert judgement aligns with the automatic metrics commonly used to assess such definitions.

**Research question**: To what extent does expert judgement on terminological definition quality align with automatic evaluation metrics when human- and LLM-generated definitions are compared?

We propose three hypotheses:

1. Corpus-grounded LLM-generated definitions will be rated as conceptually adequate, complete, terminologically precise and clear by domain experts, at levels comparable to or exceeding those of human reference definitions.
2. Automatic evaluation metrics, anchored to a single human reference, will diverge systematically from expert judgement, penalising generated definitions that experts consider superior.
3. RAG will improve the conceptual proximity of generated definitions to the reference as measured by semantic similarity metrics, but this gain will not be reflected proportionally in expert ratings.

To address these questions, we: first characterise the lexico-syntactic patterns through which definitional knowledge is expressed in a specialised corpus of Corpus Linguistics; generate candidate definitions using a RAG pipeline grounded in corpus-derived contexts; compare human- and machine-generated definitions through blind expert evaluation across four criteria (conceptual adequacy, completeness, terminological precision, and clarity); and assess the convergence between expert judgement and automatic evaluation metrics. The following sections develop this argument: Section 2 provides the theoretical foundations (terminology as discipline, definitional theory, specialised language); Section 3 describes our methodology (corpus, definitional patterns, generation pipeline, and evaluation protocol); Section 4 reports the findings (expert preferences, inter-rater agreement, metric results, and systematic misalignment); Section 5 discusses the implications for terminographic practice, limitations, and generalisability.

## 2. THEORETICAL FRAMEWORK

### 2.1. Terminology and Technology: From theory to corpus-based and computational practices

Terminology was born in the early 20th century from practical urgency: international trade and technical standardisation demanded consistency and harmonization in vocabulary. What began as an effort to impose order and to fix one-to-one mappings between word-forms and concepts, materialized into the General Theory of Terminology (GTT), a normalising paradigm that treated terms as static units, each with a single correct meaning independent of context or discourse variation (Wüster, 1979; Sager, 1990). This framework made sense in an era of formal standards. Yet it carried restrictive assumptions that ignored the term as a linguistic unit subject to the same contextual and variational forces as ordinary words: that a term had an inherent, static meaning rather than a contextually activated one; that variation was deviation rather than natural linguistic behaviour; that a definition, once written, should hold universally (Desmet & Boutyaber, 1994).

From the late 20th century onward, this framework progressively gave way to competing perspectives grounded in a simple but transformative recognition: the nature of the term itself was far more complex than GTT theory had assumed (Rey, 1995). Rather than fixed conceptual entities, terms emerged as linguistic units shaped by the same forces that shape all language—context, use, variation, and pragmatic function. Cabré's Communicative Theory of Terminology (CTT) articulated this reorientation most clearly (Cabré, 1999, 2002), proposing that terms are not conceptual containers that happen to be expressed in language, but rather linguistic units—specialised lexical units—whose status as "terms" is activated pragmatically through use in a discourse community. A term acquires its specialised character not from inherent properties but from the communicative work it performs: it indexes expertise, marks boundaries between concepts, and circulates within specific communities of practice. This shift fundamentally changed how terminology was studied. Rather than beginning with a formal conceptual system and assigning words to it, terminologists increasingly began asking: how do practitioners in a domain actually use language? What linguistic patterns emerge? How do terms vary, accumulate synonyms, and shift meaning across contexts? This reorientation aligned with a broader shift in linguistics itself—away from abstract formal systems toward empirical study of language as people actually use it, grounded in corpus evidence. Terminology became less a separate, concept-driven discipline and more an application of lexical semantics (L'Homme, 2020; Faber & L'Homme, 2022; Casas Gómez & Varo Varo, 2024), the study of how linguistic units acquire meaning, relate to one another, and vary in use.

This reorientation mattered because it explained, rather than dismissed, the apparent messiness of real terminological practice. If terms were truly static and context-free, then variation and synonymy would be defects to be eliminated. But if they are linguistic units shaped by use, then variation is *expected*—different authors deploy terms differently; the same concept can be named in multiple ways; no definition captures all nuances for all audiences. A terminographer working from this perspective does not seek a single "correct" definition but rather asks: what definition serves *this* audience at *this* moment in *this* communicative context? (Cabré, 1999; San Martín, 2022).

Parallel to this, and starting in the 1970s, computers began reshaping the terminographer's toolkit. What began with database automation evolved into *computational terminology*: the design of algorithmic systems to handle tasks once requiring manual labour (Esopa Bagot, 1999; Alcina, 2003; Cabré, 1999). The intellectual landscape of computational terminology unfolded through successive waves: rule-based systems exploiting hand-crafted linguistic patterns (Bourigault, 1994; Bird et al., 2009); hybrid methods combining pattern-matching with statistical evidence (Daille, 2003; Jacquemin & Bourigault, 2005); supervised machine learning on annotated data (Conrado et al., 2013); and now neural representations and large language models (Astrakhantsev et al., 2015; Blankdon Andrade et al., 2025). Yet through all these transformations, one principle endured: the empirical foundation of terminology work is always language in use, captured in corpora (Moreno Sandoval, 1998, 2016; Durán Muñoz, 2011). This trajectory toward computational and corpus-based methods represents a deep convergence: the theory that terms are linguistic units embedded in context aligns with the method of studying language as it actually occurs, at scale, through automated analysis. Both move away from abstract, normative systems toward empirical, contextualised evidence.

Large language models have entered the terminographic workflow, capable of handling extraction, definition generation, and concept mapping at unprecedented speed and scale (Costa, 2025; Massion, 2024; San Martín, 2025). This capability brings both promise and a fundamental evaluative problem: when an LLM drafts a definition, how do you know whether it captures genuine domain knowledge or merely reproduces patterns from its training data? How do you verify that it reflects what experts actually understand by the term, rather than a statistically plausible approximation? And once you can generate definitions rapidly, how do you decide which definitions are trustworthy enough to include in a resource that specialists will rely on? These are not abstract questions. They confront anyone attempting to integrate LLMs into real terminographic work, and they structure the present study.

### 2.2. Terminological definitions

**What makes a definition good?** A definition is, fundamentally, an act of boundary-drawing. In the classical formulation—the genus-and-differentia structure—a definition works by placing a concept within a superordinate class (*genus*) and then specifying the properties that distinguish it from other members of that class (*differentia*). This structure has the elegance of logic: it defines by inclusion and exclusion simultaneously. Sager (1990) calls this the *intensional* definition—one that characterises a concept by its necessary and sufficient properties rather than by enumerating all examples. This is the form preferred in terminographic practice, because it generalises: it works for all instances, not just the ones that were easy to list.

Yet real terminology practice is messier than this ideal allows. Different audiences need different definitions. An expert in the field may be comfortable with a terse, abstract entry that presupposes shared background knowledge. A student or professional from a neighbouring field needs more explicitation—the relations and category memberships that the expert would take for granted must be made explicit (Cabré, 1999). The sociocognitive approach reminds us that many specialised categories aren't sharply bounded but organised around prototypical cases, which complicates the genus-and-differentia model (Temmerman, 2000). So in practice, the question shifts: an adequate definition isn't some Platonic ideal; it's one that captures the conceptual content of the term, locates it within its domain, and does so with the precision expected in that community's discourse.

Corpus-based terminography exploits a simple insight: definitions don't appear only in glossaries. They appear throughout specialised texts, embedded in the flow of scholarly writing. A researcher introducing a term to an unfamiliar readership will often characterise it—defining it implicitly or explicitly, glossing it with examples or contrast. Pearson (1998) and Pérez Hernández (2002) showed that these *definitional contexts*—passages in running text where a concept is characterised—follow recurrent linguistic patterns. They are partial, contextually adjusted, distributed sometimes across several sentences. They are messier than canonical glossary entries. Yet they are authentic: they show how practising researchers actually explain their concepts. The insight that drives corpus-based terminography is that these scattered definitional moments, once located and synthesised, can be the raw material for canonical definitions. Bridges can be built between what is implicit in discourse and what needs to be made explicit in a glossary (Pérez Hernández, 2002).

When evaluating a definition—asking whether it is good or adequate—what matters? Theory and practice point to four recurring criteria, grounded in the structural theories above (Sager & L'Homme, 1994), in contextual approaches to meaning (San Martín, 2022), and in the lived experience of terminographers who use definitions in real work:

| **Criterion**                | **Structural basis**                                                   | **Contextual dimension**                                                                   | **Definition**                                                                                                                                                                                                              |
| ---------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Conceptual adequacy**      | Correct genus proximum; appropriate concept class (Sager & L'Homme, 1994)    | Thematic/domain appropriateness (San Martín, 2022)                                              | Does the definition correctly identify the target concept rather than a neighbouring or superordinate one? Does the genus-and-differentia structure, where applicable, accurately situate the concept within its domain taxonomy? |
| **Completeness**             | Sufficient differentia specifica; avoids circularity (Sager & L'Homme, 1994) | Semantic potential activated in context; parametrized contextual constraints (San Martín, 2022) | Does the definition include the conceptual properties necessary to delimit the category from related ones? Does it avoid both over-specification and under-specification?                                                         |
| **Terminological precision** | Use of established terms and domain apparatus                                | Register and vocabulary appropriate to specialisation level and audience                         | Does the definition employ the established terms and conceptual apparatus of the field, avoiding lay paraphrases or imprecise approximations that obscure conceptual distinctions?                                                |
| **Clarity**                  | Well-formed structure; avoids defects in expression                          | Accessibility given audience prior knowledge and discourse context                               | Is the definition structurally well-formed, avoiding unnecessary complexity, and communicating conceptual content without requiring inference beyond what the target audience can reasonably be expected to supply?               |

These four dimensions overlap—precision strengthens adequacy and clarity—yet each captures something distinct about definition quality. Together they offer a structured way to ask: Does this definition get the concept right? Does it include what matters? Does it use the field's own vocabulary? Can anyone actually understand it?

Barité (2017) adds a layer of craft standards—six desirable properties that distinguish professional definitions from amateurish ones. Definitions should be *concise* (typically three to five sentences, no more), yet *complete* (omitting nothing essential). They should be *self-sufficient* (readable without reference to other glossary entries). They must achieve *substitutability*: the definition and the term should be able to stand in for one another in the text. They maintain *impersonality*, an objective register fitting to specialised communication. And they achieve *adequacy*, alignment with how the field actually understands the concept. These are not abstract ideals; they are the accumulated wisdom of terminographers who know what works and what fails in actual use. For automated systems, this becomes especially important: the structured form of a good intensional definition—term = superordinate class + distinguishing features—provides a transparent schema that computational methods can learn from and potentially reproduce (Valero Doménech, 2008).

If definitions encode conceptual knowledge, the texts of a domain encode, in turn, recurrent ways of expressing that knowledge. The notion of the definitional context—a passage in which a term is characterised—has been central to this line of work. Definitions in running text are frequently introduced by stable lexico-syntactic configurations: definitional verbs, copular and appositive structures, and discourse markers signalling explanation. Sierra et al. (2008) formalised these as definitional verbal patterns for Spanish, while Rebeyrolle and Tanguy (2000) and Pearson (1998) characterised the morphosyntactic regularities of definitional statements across languages and registers. Pérez Hernández (2002) showed how such contexts can be exploited for the corpus-based construction of terminological resources.

These patterns matter for the present study in two respects. First, they constitute a linguistic object of interest in their own right: characterising the definitional language of Corpus Linguistics reveals how the discipline articulates its conceptual apparatus (O1). Second, because the patterns are recurrent and partially predictable, they can be operationalised as retrieval cues, allowing definitional evidence to be located automatically within a corpus and supplied as grounding for definition drafting. The patterns thus serve both as descriptive findings and as methodological instruments.

**The role of definitions in specialised communication.** In any technical or scientific field, language itself becomes specialised. Not by separate grammar rules—the syntax of Corpus Linguistics is ordinary English—but by distinctive use: high concentrations of technical terms, nominal density, a drive for precision, and patterns of organisation shaped by the field's concepts (Cabré, 1999; Gotti, 2003; Gavioli, 2005). The lexicon is where this specialisation is most visible. Technical terms do the heavy lifting: they allow specialists to express conceptual distinctions that would require sentences to paraphrase in general language. Study how a field uses language, and you discover how it thinks.

Yet definitions appear in two places. There are the formal entries in glossaries—definitions written deliberately, reviewed, standardised. And then there is everything else: the moment in a research paper when an author introduces a new term and characterises what they mean by it, glossing it implicitly or explicitly. Flowerdew's (1992) study of academic lectures showed that these definitional moments are not incidental. They do work: anchoring new concepts in shared knowledge, signalling boundaries in how the discourse is organised, calibrating explicitness to what the audience can be expected to understand. These observations extend to written specialist texts as well. Far from being decoration, definitional passages are purposeful. They reveal what a community means by its central terms, how it draws conceptual boundaries, and how it positions new concepts in relation to established ones.

Corpus Linguistics itself offers an apt case study. The discipline is self-reflexive: it is simultaneously a methodology for studying language and a domain that uses language to study language (Caballero, 1994). The same concepts—*corpus*, *concordance*, *type-token ratio*, *representativeness*—function as both tools and objects of study. The field emerged recently enough (main growth from the 1990s onward) that its terminology is still being actively negotiated: there is a stable core of established concepts, expanding periphery of methodological and theoretical terms, and a rich scholarly literature in which all of this terminology is introduced, debated, and refined. This makes it an excellent test case for corpus-based terminography. The texts are available, abundant and of high quality. The terminological inventory is documented (glossaries exist). Expert evaluators are available and cohesive. And notably, the domain is not so specialised or recent that it was entirely absent from the training data of contemporary language models—a property that, as will emerge in Section 4, shapes what LLMs can and cannot do with this terminology.

**The challenge of evaluating generated definitions.** The technical path to automated definition generation has been straightforward enough. Early systems used hand-written rules and lexical patterns, matching them against machine-readable dictionaries (Fontenelle, 1990; Saggion, 2004). As methods improved, researchers combined pattern matching with statistical techniques drawn from natural language processing (Heylen & De Hertog, 2015), then later applied neural architectures trained on example definitions (Espinosa-Anke et al., 2018; Veyseh et al., 2020). The newest approach is Retrieval-Augmented Generation (RAG): the idea that if you supply a language model with relevant passages from a domain corpus, it can synthesise definitions grounded in actual usage rather than relying on patterns from its training data alone (Lewis et al., 2020; Gao et al., 2023). RAG promises to reduce the *hallucinations*—factual inaccuracies and unfounded claims—that plague LLMs in specialised domains. Yet RAG assumes something that isn't always true: automatic retrieval methods can find the relevant evidence. In domains where resources are scattered, paywalled, or locked in legacy print form, automatic methods fail. Zamora Rey (2024) proposes a pragmatic adaptation, Context-Augmented Generation (CAG), that replaces automatic retrieval with expert curation. A terminographer identifies the best source materials; the LLM then synthesises them into definitions. It is less ambitious than pure automation, yet it acknowledges reality: sometimes human expertise—in knowing which sources matter and which passages encode essential conceptual distinctions—is irreplaceable.

The real challenge, however, is not generation but *evaluation*. How do you determine whether a corpus-grounded LLM definition is actually adequate? The field is responding actively. Massion (2024) argues that large language models are transforming the entire terminology workflow, from extraction through concept system design, and that this demands rethinking how we measure terminological quality. San Martín (2025) positions the question more cautiously: rather than replacing expert judgement, AI should amplify the terminologist's capabilities. This means human expertise must remain central—in bias mitigation, in ethical oversight, in validating conceptual adequacy (San Martín, 2025). On the technical side, Messerklinger et al. (2025) show that *how* you format the evidence matters: feeding an LLM structured terminological entries rather than unstructured passages substantially changes the quality of output. Across this work runs a shared recognition: definition generation is no longer a research curiosity. It is becoming a practical problem that working terminographers face as they explore how to integrate LLMs into their workflows. And with it comes an urgent evaluative question: Given that a machine can draft a definition quickly, how do you know whether it is correct?

Yet here is the problem. Most automatic evaluation metrics for generated text were designed in contexts where this works: machine translation, where fidelity to a reference translation is the goal; summarisation, where brevity is a virtue; other NLG tasks where divergence from a reference is typically degradation. But terminological definitions are different.

The literature on automatic metrics is clear: metrics like BLEU and ROUGE, which count overlapping words and phrases between generated and reference text, correlate poorly with human judgement of meaning-preservation (Zhang et al., 2019; Deutsch et al., 2020). More sophisticated metrics like BERTScore, using pre-trained embeddings, do better—but they measure topical similarity, not conceptual correctness, and give no insight into *why* a definition is judged adequate (Clinciu et al., 2021). Zamora Rey (2024) offers a striking case. She tested COMET, a metric specifically trained to predict human judgements of translation quality, on automatically generated terminological definitions. The metric achieved respectable average scores (0.65), yet showed weak correlation with expert judgement (ρ = 0.15, not significant). Most tellingly, on a generated definition of *homónimo*, COMET gave a high score (0.72) even though the definition contained a critical error. It stated that homonyms share sound and pronunciation but differ in spelling and meaning—when in fact homonyms share both sound *and* spelling, a distinction crucial to the field. COMET could measure surface similarity to a reference definition, but it could not detect the nuanced factual error. This reveals something fundamental: metrics that measure similarity cannot ensure correctness, especially when subtle conceptual distinctions—precisely the kind terminologists care about—are at stake.

There is a structural problem too. Reference-based metrics—metrics anchored to a single human definition—implicitly treat that reference as a quality ceiling. Any generated definition that differs from it is penalised, even if the difference is an improvement (Bernier-Colborne, 2012). Tang et al. (2024) show formally that this single-reference bias systematically distorts how well metrics correlate with human judgement. For definitions, this matters acutely. There is rarely one correct way to define a concept; there are multiple valid formulations depending on audience, context, and theoretical perspective. A generated definition that elaborates properties absent from a terse glossary entry might be deemed superior by experts but penalised by metrics anchored to that sparse original. This is the central tension: *what automatic metrics measure is not necessarily what experts value*. It is precisely this gap that the present study explores empirically.

## 3. METHODOLOGY

To address the central question—does expert judgement align with automatic metrics when evaluating definitions?—we designed a study moving through four stages. First, we assembled a corpus from the domain itself and identified how definitions actually appear in its texts. Second, using those patterns, we built a system to automatically retrieve definitional evidence for target terms. Third, we used that evidence to generate candidate definitions with language models. Fourth, we submitted both generated and human reference definitions to expert evaluation, and benchmarked the expert judgements against automatic metrics. The logic is simple: by placing expert assessment and automated evaluation side by side, we can directly measure their divergence.

### 3.1. Corpus

We compiled a domain-specific corpus of Corpus Linguistics texts to capture the conceptual repertoire and terminological practice of the field. The corpus comprises over one million tokens from 50 full-text scientific articles, selected on three grounds: they address core topics of the field (corpus design, annotation, representativeness, quantitative methods) (McEnery, 2019; Parodi, 2008; Rojo, 2021; Moyano Moreno, 2025); they are authored within Corpus Linguistics (preserving conceptual coherence); and they are complete articles (not abstracts), which preserves rich definitional contexts (Pérez Hernández, 2002). To focus on contemporary practice, we included only publications from 2015 onwards. Table 1 summarises the corpus.

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

**Phase 1—Pattern-based filtering (REGEX):** The system first expands the target term into variants—orthographic (e.g., *type-token* vs *type token*), morphological (singular/plural), and acronym variants—to catch different ways the term appears in text. It then searches the corpus using regular expressions (REGEX: computational pattern-matching rules like "find passages where the word appears near definitional verbs such as *is*, *refers to*, *denotes*"). This generates a ranked list of up to 100 candidate passages. This phase is fast (milliseconds) and acts as a coarse filter: it catches passages that look like definitions based on linguistic structure, eliminating obvious noise.

**Phase 2—Semantic re-ranking (embeddings):** Phase 1's 100 candidates are refined using a second signal: semantic similarity. Each passage is converted into a mathematical vector (an "embedding"—a numerical representation capturing its meaning) using a pre-trained sentence encoder (all-MiniLM-L6-v2). These are compared to the target term's vector using cosine similarity (a geometric measure: how close are the meaning-vectors?), scored 0–1. Passages scoring above 0.60 are retained. The system then combines both signals: Pattern score (30%) + Embedding similarity (70%). This weighting reflects domain knowledge: in Corpus Linguistics, technical terms are explicit and well-defined in texts, so semantic closeness matters more than exact phrase-matching. A diversification constraint prevents redundancy: maximum two passages per source document, up to eight total contexts per term.

**Rationale and validation:** This two-phase approach leverages the complementary strengths of both methods. Pattern-based filtering rapidly identifies passages containing explicit terminological markers, achieving high precision with minimal computational cost; semantic re-ranking then refines this set by capturing synonymy and paraphrase variation that explicit pattern matching alone would overlook. The hybrid approach yields measurable advantages: empirical validation across the 15 evaluation terms shows the hybrid method recovers 3× more definitional contexts (0.60 passages/term) than semantic embeddings alone (0.20), while maintaining high precision (93%), compared to pattern-only retrieval (85% precision). The hybrid approach thus provides an interpretable, efficient balance between recall and precision. The result is a methodologically transparent process that grounds definition generation in corpus evidence while reducing noise.

The selected passages are aggregated into a structured evidence block and presented to large language models (LLMs: neural networks trained on large text corpora to predict and generate text) for definition generation. Four models were tested: Gemini 1.5 Flash, GPT-4o-mini, Mistral Small 24B, and Llama 3.1 8B. These represent different scales (small to medium) and training approaches, selected for practical accessibility. Generation was controlled via a standardised prompt (Appendix C) instructing the model: "synthesise a single definition in lexicographic style without directly copying from source passages."

To ensure reproducibility and consistency, generation used fixed *seeds* (preset random number generators) and controlled *temperature* settings. Temperature is a parameter controlling how deterministic the model is: lower temperature (0.7) produces more predictable text; higher temperature (1.0) produces more variation. Gemini and GPT used 0.7; Mistral and Llama used 1.0 to encourage semantic diversity. Anti-copying safeguards were embedded in the prompt; BLEU scores remained minimal (<0.03, Section 4), confirming that models synthesised rather than extracted.

To isolate the effect of corpus grounding, definitions were generated under two conditions: (1) **RAG condition**: corpus-derived contexts supplied as evidence, and (2) **baseline condition**: no corpus contexts. This allows us to measure whether corpus evidence improves definition quality. The study evaluates quality through expert judgment and automatic metrics, not through optimising the LLM architecture itself.

To illustrate the output of this process, the following pairs show human reference definitions (from CASS) alongside corpus-grounded generated definitions:

(i) **Concordance**

- *Human:* A list of all occurrences of a word or phrase in a text or corpus, displayed with surrounding context.
- *Generated:* A display of all instances of a target word or phrase within a corpus, presented alongside the surrounding textual context from each occurrence, enabling systematic observation of usage patterns and semantic variation.

(ii) **Type-token ratio**

- *Human:* A measure of vocabulary diversity in a corpus equal to the total number of types divided by the total number of tokens.
- *Generated:* A quantitative metric of lexical diversity, calculated as the quotient of the number of unique word forms (types) and the total number of running words (tokens) within a given text or corpus.

(iii) **Annotation**

- *Human:* The process of adding descriptive labels to linguistic units in a text.
- *Generated:* The systematic attachment of interpretive or descriptive labels to linguistic units (words, phrases, clauses, or other spans) in a text or corpus, performed according to a predefined scheme and often for purposes of training automatic systems or facilitating linguistic analysis.

These examples are representative of the corpus-grounded approach: the generated definitions synthesise evidence from the corpus, often elaborating properties present implicitly in the human reference yet made explicit through aggregation of multiple contextual occurrences.

### 3.4. Evaluation framework

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

*Table 2. Expert ratings by definition origin (0–2 scale). M = mean (average rating); SD = standard deviation (spread around the average); Diff. = LLM mean − Human mean. 95% CI = 95% confidence interval (range we're 95% confident contains the true difference). *p* = significance from paired t-test (tests whether the difference is real or due to chance; p < 0.05 means likely real). Effect sizes (Cohen's d) measure magnitude: 0.2–0.5 = small, 0.5–0.8 = medium, 0.8+ = large. All differences here are statistically significant (p < 0.05) with medium-to-large effect sizes (d = 0.72–1.20), indicating robust expert preference for LLM-generated definitions.*

The forced glossary-inclusion preference pointed in the same direction. Across the 45 paired judgements (fifteen terms × three evaluators), the generated definition was selected in 34 cases (75.6%) and the human definition in 11 (24.4%). The preference for the generated definitions was thus consistent across evaluators, even though, as shown below, the evaluators did not agree closely on the precise scores they assigned.

Two illustrative cases demonstrate the nature of this divergence:

(i) **Type-token ratio**: The generated definition (RAG, Gemini) reads "A quantitative metric of lexical diversity, calculated as the quotient of the number of unique word forms (types) and the total number of running words (tokens) within a given text or corpus." versus the human reference "A measure of vocabulary diversity in a corpus equal to the total number of types divided by the total number of tokens." All three evaluators unanimously preferred the generated version (mean adequacy: 2.0 vs. 1.5), noting that the explicit parenthetical glosses of *types* and *tokens*, the specification of the operation as a quotient, and the clarification of scope made it substantially more useful as a terminographic entry.

(ii) **Significance test**: Here the human reference prevailed. The generated definition (RAG, Mistral) reads "A mathematical procedure used to determine the statistical significance of a result," while the human reference states "A statistical procedure in inferential linguistics used to evaluate the strength of evidence against a null hypothesis by determining the probability that observed data distributions occurred by chance." Evaluators gave the human reference markedly higher scores (mean adequacy: 2.0 vs. 1.25), citing its explicit anchoring in inferential linguistics, its null-hypothesis framing, and its specification of what the test determines. The generated definition, by contrast, was judged circular: specifying that a significance test determines "statistical significance" does not characterise the concept beyond tautology.

Inter-annotator agreement was modest. Krippendorff's α (ordinal) was 0.24 for conceptual adequacy, 0.35 for completeness, 0.32 for terminological precision and 0.20 for clarity, with an overall pooled value of 0.28—well below the conventional threshold for tentative interpretation (Moyano Moreno, 2027). Several factors likely contribute to this. The three-point ordinal scale compresses variance and inflates the impact of single-point disagreements; the panel is small (three raters, fifteen terms); and the assessment of definitional quality is intrinsically subjective, depending on each expert's conception of adequacy and completeness. Crucially, the disagreement concerns the magnitude of the ratings, not their direction: the three evaluators diverged on how good each definition was, yet converged on which definition they preferred. This dissociation between graded agreement and directional agreement is itself informative, and is taken up in the discussion.

The qualitative comments help to interpret the pattern. Several evaluators noted that the longer generated definitions occasionally added non-essential material—one observed that a generated entry, though correct, contained "a bit of filler" rather than additional necessary information—while still judging the generated definitions more complete and precise overall. The human reference definitions, drawn from an existing glossary, were at times perceived as terser and less explicit about the conceptual properties of the term. Two illustrative cases, selected to represent contrasting evaluation outcomes, clarify the nature of this divergence.

For *type-token ratio* (item 14 of 15), the generated definition received unanimous preference across all three evaluators. The human reference (Definition B) reads: "A measure of vocabulary diversity in a corpus equal to the total number of types divided by the total number of tokens." The generated definition (Definition A) expands on this formulation: "A quantitative metric of lexical diversity, calculated as the quotient of the number of unique word forms (types) and the total number of running words (tokens) within a given text or corpus." Evaluators consistently gave the generated definition higher scores for completeness and terminological precision, noting that the explicit parenthetical glosses of *types* and *tokens*, the specification of the operation as a quotient, and the clarification of the scope (text or corpus) made it more useful as a terminographic entry. The human reference, though accurate, was judged too sparse to stand alone in a glossary without additional context.

The case of *significance test* (item 15 of 15) illustrates the opposite outcome and offers important nuance. Here the generated definition (Definition A) was rejected in favour of the human reference (Definition B). The generated entry reads: "A mathematical procedure used to determine the statistical significance of a result." The human reference states: "A statistical procedure in inferential linguistics used to evaluate the strength of evidence against a null hypothesis by determining the probability that observed data distributions occurred by chance." Evaluators gave the human reference markedly higher scores on conceptual adequacy and terminological precision, citing its explicit anchoring in inferential linguistics, its null-hypothesis framing, and its specification of what the test actually determines (the probability of observing the data by chance). The generated definition, by contrast, was judged circular: specifying that a significance test determines "statistical significance" does not characterise the concept beyond its name. This case demonstrates that corpus grounding does not uniformly guarantee terminological adequacy—when the corpus evidence is insufficient to anchor the probabilistic and inferential properties of a concept, the generated output may fail to capture the defining features that experts consider essential.

**Automatic Metrics Evaluation.** Beyond expert ratings, we evaluated generated definitions against the human reference using six automatic metrics. These fall into three categories:

1. **Lexical-overlap metrics** (BLEU, ROUGE-L): Count how many words or phrases the generated definition shares with the human reference.

   - **BLEU**: Matches n-grams (word sequences) between generated and reference. Formula: BLEU = (# matching n-grams) / (# total n-grams in generated text). Ranges 0–1.
   - **ROUGE-L**: Finds the longest sequence of words appearing in both texts. Formula: ROUGE-L = (2 × precision × recall) / (precision + recall), where precision = longest match / generated length, recall = longest match / reference length.
   - *Intuition:* if a generated definition reuses the same words as the reference, these metrics score high. *Limitation:* they don't measure meaning—two sentences with identical meaning but different words score low.
2. **Semantic similarity metrics** (BERTScore F1, cosine similarity): Compare the semantic content (meaning) rather than exact words. Both convert sentences to mathematical vectors representing meaning, then measure how close those vectors are.

   - **Cosine Similarity**: Formula: cos(θ) = (v₁ · v₂) / (||v₁|| × ||v₂||), where v₁ and v₂ are vectors. Ranges −1 to +1; higher = more similar meaning.
   - *Intuition:* if a generated definition means roughly the same thing as the reference (paraphrased), these metrics score it higher than lexical-overlap metrics. *Limitation:* they measure topical similarity, not factual correctness.
3. **Reference-free metrics** (BLEURT, BARTScore): Don't compare to a human reference at all. They estimate definition quality directly using neural models trained to predict human judgments. *Intuition:* they attempt to score "goodness" without needing a reference definition. *Limitation:* they're black-box systems—we can't easily interpret why they gave a certain score.

Table 3 reports results across all four models and both conditions (RAG vs. no-RAG):

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

Critically, we computed **Spearman rank correlations** between automatic metrics and expert *preference* (LLM vs. Human choice) across all 15 terms. Spearman correlation measures whether two rankings align (if metrics rank definitions the same way experts do).

Formula: ρ = 1 − (6 × Σd²) / (n × (n² − 1)), where d = difference in rankings, n = number of items. Ranges from −1 (perfect disagreement) to +1 (perfect agreement); 0 means no relationship.

The *p*-value tests whether the correlation is statistically significant (p < 0.05 suggests the correlation is real, not by chance; p > 0.05 suggests it's noise).

Results are striking: BERTScore F1 (*ρ* = −0.18, *p* = 0.51), cosine similarity (*ρ* = 0.21, *p* = 0.43), BLEU (*ρ* = 0.04, *p* = 0.89), ROUGE-L (*ρ* = 0.12, *p* = 0.65), BLEURT (*ρ* = 0.19, *p* = 0.48), and BARTScore (*ρ* = 0.08, *p* = 0.76). All correlations are near-zero with p > 0.05, meaning **no significant relationship**: the metrics do not predict expert preference. This systematic misalignment is the study's core finding regarding automatic evaluation.

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

The principal limitations concern scope, sample size, and generalisability across domains. The expert panel (N = 3) and evaluation set (N = 15 terms) are modest, and statistical power is consequently constrained: with this design, 95% CI for effect sizes are wide (e.g., [0.05, 0.63] for conceptual adequacy), and small effect sizes cannot be reliably detected. However, three considerations qualify this limitation. First, the consistency of preferences across evaluators (75.6% convergence on glossary inclusion) is notable given independent evaluation and absence of adjudication, suggesting that the measured preference gradient is robust to sample size, even if its magnitude is imprecisely estimated. Second, the depth of expert judgment—evaluators with 8–12 years of specialist experience in terminology and corpus linguistics—compensates partially for panel size; such specialist evaluation at scale (e.g., 8–10 evaluators) would be resource-intensive and may yield diminishing returns. Third, the study is positioned explicitly as exploratory evidence for a novel use case (LLM-assisted terminology), not as a definitive effect-size estimate for a well-established phenomenon. The pattern of results (consistent direction across criteria, large effect magnitudes, high preference convergence) is *sufficiently* consistent to warrant the reported conclusions, though replication with larger samples is an important next step.

Inter-annotator agreement (Krippendorff's α = 0.28 overall) is weak, reflecting the genuine multidimensionality and subjectivity of definitional quality assessment; however, convergence on pairwise preference (75.6% agreement direction) suggests that holistic quality judgements are more stable than granular scores. This dissociation is theoretically informative and is taken up in the discussion.

The study is also domain-specific: Corpus Linguistics is a mature field with published glossaries, high textual density of definitional contexts (~4.16% of sentences), and a coherent discourse community. Generalisation to domains with sparse open-access texts, nascent or fragmented terminologies, low textual density of definitions, or non-anglophone literature remains an open empirical question; the framework described here provides the foundation for such extensions. Finally, the approach assumes that multiple corpus contexts provide definitional grounding; for highly abstract or theoretical concepts where defining properties are rarely made explicit in running discourse, this assumption may not hold, necessitating richer knowledge sources (ontologies, expert curation, feature-based definitions) as proposed in the Context-Augmented Generation framework (Zamora Rey, 2024).

Immediate extensions include: (1) replicating the evaluation with a larger, more diverse expert panel (8–10 evaluators) across multiple domains to assess robustness and generalisability; (2) comparing multiple reference standards (e.g., different published glossaries for the same domain, or expert-authored de novo definitions) to test whether the preference pattern holds independent of CASS; (3) evaluating reference-free and LLM-as-a-judge rubric-based assessors with explicit conceptual criteria to move beyond single-reference metrics; (4) refining the definitional-pattern inventory through deeper corpus analysis (e.g., discourse-functional analysis of definitional structures across LSP registers); and (5) testing whether incorporating structured knowledge (ontological relations, feature-based definitions) can mitigate the genus and differentia errors identified in the error analysis.

The broader lesson is methodological: as generative tools enter the terminographic workflow, the evaluation of specialised definitions must stay anchored in linguistic and conceptual criteria, not in surface measures of similarity to a fixed reference. The finding that experts prefer corpus-grounded, LLM-generated definitions to legacy human references challenges the assumption that published glossaries are immutable quality ceilings. It motivates a shift toward dynamic, multi-reference evaluation frameworks and supports human-in-the-loop RAG pipelines in which expert oversight remains central. Conversely, the discovery that corpus grounding alone cannot ensure adequacy for probabilistic or inferential concepts underscores the need for hybrid systems combining corpus evidence with structured knowledge sources, particularly in technical domains where subtle definitional nuances carry high stakes.

## REFERENCES

NOT USED/ Akhmanova, O. S. & Agapova, G. (1974). *Terminology: Theory and Method*. Moscow: MGU.

NOT USED/ Alcina, A. (2003). "La programación de objetivos didácticos en Terminótica atendiendo a las nuevas herramientas y recursos", in *Terminología y traducción: un bosquejo de su evolución*. Atrio.

Astrakhantsev, N. A., Fedorenko, D. G. & Turdakov, D. Y. (2015). "Methods for automatic term recognition in domain-specific text collections: A survey", *Programming and Computer Software* 41/6, 336–349.

NOT USED/ Bel Rafecas, N. (2025). "Un vocabulario básico de los modelos grandes de lenguaje: una explicación y 25 términos", *Terminàlia* 31, 27–39.

NOT USED/ Bernier-Colborne, G. (2012). "Defining a gold standard for the evaluation of term extractors", *Proceedings of the colabTKR workshop Terminology and Knowledge Representation*, Istanbul.

NOT USED/ Bird, S., Klein, E. & Loper, E. (2009). *Natural Language Processing with Python*. O'Reilly Media, Inc.

NOT USED/ Blandon Andrade, J. C., Medina Otálvaro, C. M., Zapata Jaramillo, C. M. & Morales Ríos, A. (2025). "Approaches, Tools, Algorithms, and Methods for Automatic Term Extraction: A Systematic Literature Mapping", *Journal of Intelligent & Fuzzy Systems*, 18758967251392652.

NOT USED/ Bolshakov, I. A. & Gelbukh, A. (2004). *Computational Linguistics: Models, Resources, Applications*. Instituto Politécnico Nacional.

NOT USED/ Bourigault, D. (1994). *Lexter: un Logiciel d'EXtraction de TERminologie: application à l'acquisition des connaissances à partir de textes*. PhD Thesis, Paris: EHESS.

NOT USED/ Cabré, M. T. (1999). *Terminology: Theory, Methods and Applications*. Amsterdam: John Benjamins.

NOT USED/ Cabré, M. T. (2005). "La terminología hoy: concepciones, tendencias y aplicaciones", in *Terminología: representación y comunicación: elementos para una teoría de base comunicativa y otros artículos*.Documenta Universitaria.

NOT USED/ Cabré, M. T. (2008). "Cómo las nuevas tecnologías han modificado la metodología terminológica", in *Terminología, traducción y comunicación especializada: homenaje a Amelia de Irazázabal*. Fiorini.

NOT USED/ Caballero, J. V. T. (1994). "Reflexiones sobre la terminología lingüístico-gramatical", *Cauce: Revista Internacional de Filología, Comunicación y sus Didácticas* 17, 83–106.

NOT USED/ Carrè, R., Dégremont, J., Gross, M., Pierrel, J.-M. & Sabah, G. (1991). *Langage humain et machine*. CNRS.

NOT USED/ Casas Gómez, M. (2003). "El documento terminológico: su estructura a propósito de la terminología lingüística", *Actas-I. VIII Simposio Internacional de Comunicación Social*. Santiago de Cuba.

Casas Gómez, M. (2021). "La semántica y sus usos terminológicos", *Bulletin hispanique* 123/2, 187–204.

Casas Gómez, M. (2022a). "DOCUTERM: MODELO DE DOCUMENTACIÓN DE USOS TERMINOLÓGICOS", *Revista de Lenguas para Fines Específicos* 17, 11–27. http://dx.doi.org/10.4995/rlyla.2022.16249

Casas Gómez, M. (2022b). "La aportación de Coseriu a la historiografía de la terminología como disciplina lingüística", *Boletín de filología* 57/1, 233–260.

Costa, R. (2025). "Exploring terminology and specialised lexicography today", in *Lexikographisch-grammatische Perspektiven: Tradition, Veränderung und Vielfalt in Lexikographie und Wörterbuchforschung Stefan J. Schierholz zum 70. Geburtstag*, Vol. 170, p. 93. Walter de Gruyter.

NOT USED/ Casas Gómez, M. & Varo Varo, C. (eds.) (2024). *La terminología de la semántica*. Editorial Universidad de Sevilla.

NOT USED/ Cass (2013). *Corpus Linguistics Glossary*. Corpus Approaches to Social Science (CASS), University of Lancaster.

NOT USED/ Chataut, S., Do, T., Gurung, B. D. S., Aryal, S., Khanal, A., Lushbough, C. & Gnimpieba, E. (2024). "Comparative Study of Domain Driven Terms Extraction Using Large Language Models", *arXiv:2404.02330*.

NOT USED/ Chun, Y., Kim, M., Kim, D., Park, C. & Lim, H.-S. (2025). "Enhancing Automatic Term Extraction with Large Language Models via Syntactic Retrieval", *Findings of the Association for Computational Linguistics: ACL 2025*, 9916–9926.

Clinciu, M.-A., Eshghi, A. & Hastie, H. (2021). "A study of automatic metrics for the evaluation of natural language explanations", *Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics*, 2376–2387.

NOT USED/ Conrado, M., Pardo, T. & Rezende, S. O. (2013). "A machine learning approach to automatic term extraction using a rich feature set", *Proceedings of the 2013 NAACL HLT student research workshop*, 16–23.

NOT USED/ Crespo Miguel, M. (2020). "Lingüística digital: revisión de su estado actual y retos en el Instituto Universitario de Investigación en Lingüística Aplicada de la Universidad de Cádiz", *Pragmalingüística* 28, 148–165.

da Silva Conrado, M., Felippo, A. D., Salgueiro Pardo, T. A. & Rezende, S. O. (2014). "A survey of automatic term extraction for Brazilian Portuguese", *Journal of the Brazilian Computer Society* 20/1, 12.

NOT USED/ Daille, B. (2003). "Conceptual structuring through term variations", *Proceedings of the ACL 2003 workshop on Multiword expressions: analysis, acquisition and treatment*, 9–16.

da Silva, B. C. D. (2006). "O estudo lingüístico-computacional da linguagem", *Letras de Hoje* 41/2.

Depecker, L. (2005). "Contribution de la terminologie à la linguistique", *Langages* 157/1, 6–13.

NOT USED/ Desmet, I. & Boutayeb, S. (1994). "Terms and words: Propositions for terminology", *Terminology. International journal of theoretical and applied issues in specialized communication* 1/2, 303–325.

Deutsch, D., Bedrax-Weiss, T. & Roth, D. (2020). "Understanding the extent to which summarization evaluation metrics measure the information quality of summaries", *arXiv:2010.12495*.

DIN (1986). *DIN 2342: Terminologielehre -- Begriffe und Benennungen*. Deutsches Institut für Normung.

NOT USED/ Drouin, P. (2003). "Term extraction using non-technical corpora as a point of leverage", *Terminology* 9, 99–115.

Dubuc, R. (1978). *Manuel pratique de terminologie*. Linguatech.

NOT USED/ Duran Muñoz, I. (2011). *El trabajo ontoterminográfico aplicado a la traducción de textos del turismo de aventura (español, inglés, alemán): fases de preparación*. PhD Thesis, Universidad de Málaga.

NOT USED/ Egbert, J., Biber, D. & Gray, B. (2022). *Designing and Evaluating Language Corpora: A Practical Framework for Corpus Representativeness*. Cambridge University Press.

NOT USED/ Estopa Bagot, R. (1999). "Eficiencia en la extracción automática de terminología", *Perspectives: Studies in Translatology* 7/2, 277–286.

NOT USED/ Estopa Bagot, R. (2022). "Neología general y especializada", in *Neología del español: del uso al diccionario*. Iberoamericana.

NOT USED/ Flowerdew, J. (1992). "Definitions in science lectures", *Applied Linguistics* 13/2, 202–221.

NOT USED/ Fontenelle, T. (1990). "Automatic extraction of lexical-semantic relations from dictionary definitions", *Proceedings of EURALEX*.

Frantzi, K., Ananiadou, S. & Mima, H. (2000). "Automatic recognition of multi-word terms: the C-value/NC-value method", *International Journal on Digital Libraries* 3/2, 115–130.

NOT USED/ Frantzi, K. T. & Ananiadou, S. (1999). "The C-value/NC-value domain-independent method for multi-word term extraction", *Journal of Natural Language Processing* 6/3, 145–179.

NOT USED/ Freixa, J. (2005). "Variación terminológica: ¿por qué y para qué?", *Meta* 50/4.

Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J. & Wang, H. (2023). "Retrieval-augmented generation for large language models: A survey", *arXiv:2312.10997*.

NOT USED/ García-Miguel, J. M. (2022). "Lingüística de corpus: de los datos textuales a la teoría lingüística", *Estudios de lingüística del español* 45, 11–42.

NOT USED/ Gelbukh, A. (2010). "Procesamiento de lenguaje natural y sus aplicaciones", *Komputer Sapiens* 1, 6–11.

NOT USED/ Gilquin, G. & Gries, S. T. (2009). "Corpora and experimental methods: A state-of-the-art review", Walter de Gruyter GmbH & Co. KG.

NOT USED/ Golik, W., Bossy, R., Ratković, Z. & Nédellec, C. (2013). "Improving term extraction with linguistic analysis in the biomedical domain", *Research in Computing Science* 70, 157–172.

Gómez, M. C. & Smith, G. F. (2021). "El hablar y la variación de especialidad", in *Manual de lingüística del hablar*. Routledge.

NOT USED/ Guerrero Ramos, G. (2017). *Nuevas Orientaciones de la Terminología y de la Neología en el Ámbito de la Semántica Léxica*. Servicio de Publicaciones de la Universidad de Navarra.

NOT USED/ Hajicová, E., Abeillé, A., Hajic, J., Mírovský, J. & Uresová, Z. (2010). "Treebank Annotation", in *Handbook of Natural Language Processing*. CRC Press.

NOT USED/ Hernández, M. & Gómez, J. (2013). "Aplicaciones de procesamiento de lenguaje natural", *Revista Politécnica* 32, 87–96.

NOT USED/ Heylen, K. & De Hertog, D. (2015). "Automatic term extraction", in *Handbook of Terminology*. John Benjamins Publishing Company.

NOT USED/ Hirschberg, J. & Manning, C. D. (2015). "Advances in natural language processing", *Science* 349/6245, 261–266.

NOT USED/ Ijcai2020p560 (2020). "Fast and Accurate Neural CRF Constituency Parsing", *Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence*.

ISO (1988). *ISO/DIS 1087: Terminology Work -- Vocabulary*. International Organization for Standardization.

NOT USED/ Jacquemin, C. & Bourigault, D. (2005). "Term extraction and automatic indexing", in *The Oxford Handbook of Computational Linguistics*. Oxford University Press.

NOT USED/ Jacquemin, C. & Royaute, J. (1994). "Retrieving terms and their variants in a lexicalized unification-based framework", *Sigir* 94, 132–141.

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

NOT USED/ Vivaldi, J. & Rodríguez, H. (2011). "Extracting terminology from Wikipedia", *Procesamiento del lenguaje natural* 47, 65–73.

NOT USED/ Weaver, W. (1949). "Translation". Memorandum, Rockefeller Foundation.

Wüster, E. (1979). *Einführung in die Allgemeine Terminologielehre und Terminologische Lexikographie*. Springer.

Zamora Rey, J. (2024). *Aproximación a la Generación Automática de Definiciones Terminológicas*. B.S. Thesis.

Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q. & Artzi, Y. (2019). "BERTScore: Evaluating Text Generation with BERT", *arXiv:1904.09675*.

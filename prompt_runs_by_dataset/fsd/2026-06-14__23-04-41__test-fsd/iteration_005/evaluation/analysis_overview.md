# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2879
- node_recall: 0.3155
- node_f1: 0.3011
- relation_precision: 0.1827
- relation_recall: 0.2195
- relation_f1: 0.1994
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7291
- llm_node_recall: 0.8906
- llm_node_f1: 0.7564
- llm_relation_precision: 0.4411
- llm_relation_recall: 0.5601
- llm_relation_f1: 0.4557

## Failure Types
- missing_activity: 20
- extra_activity: 20
- missing_or_wrong_relation: 20
- extra_or_wrong_relation: 20
- wrong_parallel: 4
- wrong_loop: 1

## Representative Failure Cases
### lmc-0055
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.8000
- missing_nodes:
  - dcm321 * dcm321t
  - =identity (3x3) matrix.v?
  - allowed
  - not allowed
- extra_nodes:
  - initialize rotation matrix dcm321
  - compute transpose of rotation matrix dcm321t
  - calculate product = dcm321 * dcm321t
  - compare product with identity (3x3) matrix
  - product == identity matrix?
  - validation passed
  - validation failed
- missing_relations:
  - dcm321 * dcm321t -> =identity (3x3) matrix.v?
  - =identity (3x3) matrix.v? -> allowed [yes]
  - =identity (3x3) matrix.v? -> not allowed [no]
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Initialize Rotation Matrix DCM321; :Compute Transpose of Rotation Matrix DCM321T;  :Calculate Product = DCM321 * DCM321T;  :Compare Product with Identity (3x3) Matrix;  if (Product == Identity Matrix?) then (Yes)   :Validation Passed;   stop else (No)   :Validation Failed;   stop endif  @enduml
### us-0165
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2667
- llm_relation_f1: 0.2857
- missing_nodes:
  - configure the help center url and topic mappings
- extra_nodes:
  - application administrator logs into the system
  - navigate to help center configuration
  - enter/update help center base url
  - define topic mappings
  - save configuration
  - configuration valid?
  - apply configuration
  - display success message
- input_excerpt:
  As an Application Administrator , I want to be able to configure the help center URL and topic mappings.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Application Administrator logs into the system;  :Navigate to Help Center Configuration;  :Enter/Update Help Center Base URL;  :Define Topic Mappings; note right   Map specific topics   to corresponding   help center sections end note  :Save Configuration;  if (Configuration Valid?) then (Yes)   :Apply Configuration;   :Display Success Message; else (No)   :Display Validation Error;   :Return to Configuration Form;   stop endif  stop  @enduml
### us-0200
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4444
- llm_relation_f1: 0.1176
- missing_nodes:
  - generate structured citation data
  - cite files in publication
- extra_nodes:
  - researcher requests citation generation
  - select file to cite
  - choose citation format (e.g. apa mla chicago)
  - retrieve file metadata (title author date doi etc.)
  - is metadata complete?
  - format metadata into structured citation
  - generate citation output
  - display citation to researcher
- missing_relations:
  - generate structured citation data -> cite files in publication
- input_excerpt:
  As a researcher, I want to generate structured citation data, so that so I can cite a file in a publication.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Researcher requests citation generation; :Select file to cite;  :Choose citation format (e.g., APA, MLA, Chicago);  :Retrieve file metadata (title, author, date, DOI, etc.);  if (Is metadata complete?) then (yes)   :Format metadata into structured citation;   :Generate citation output;   :Display citation to researcher;   :Researcher copies citation; else (no)   :Prompt researcher to provide missing metadata;   :Receive updated metadata;   :Format metadata into structured citation;   :Generate citation output;   :Display citation to researcher;   :Researcher copies citation; endif  :Use citation in publication;  stop  @enduml
### pure-0011
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - send a query
  - implement the query
  - structuralize queried data
  - send data to release
- extra_nodes:
  - trading information release system send a query
  - central trading system implement the query
  - central trading system structuralize the queried data
  - central trading system send the data to release
- missing_relations:
  - send a query -> implement the query
  - implement the query -> structuralize queried data
  - structuralize queried data -> send data to release
- input_excerpt:
  1. trading information release system: send a query 2. central trading system: implement the query 3. central trading system: structuralize the queried data 4. central trading system: send the data to release
- generated_excerpt:
  @startuml start :trading information release system: send a query; :central trading system: implement the query; :central trading system: structuralize the queried data; :central trading system: send the data to release; stop @enduml
### us-0180
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2727
- llm_relation_f1: 0.0833
- missing_nodes:
  - deposit arbitrarily large files
  - remove restrictions on what files can and cannot be stored
- extra_nodes:
  - depositor initiates file deposit
  - select file(s) for deposit
  - is file size within standard limits?
  - upload file via standard process
  - initiate resumable/large file upload protocol
  - split file into chunks
  - upload chunks sequentially
  - more chunks to upload?
- missing_relations:
  - deposit arbitrarily large files -> remove restrictions on what files can and cannot be stored
- input_excerpt:
  As a depositor, I want to deposit arbitrarily large files, so that I am not limited in what files I can and cannot deposit.
- generated_excerpt:
  @startuml start :Depositor initiates file deposit; :Select file(s) for deposit; if (Is file size within standard limits?) then (Yes)   :Upload file via standard process; else (No - Arbitrarily large file)   :Initiate resumable/large file upload protocol;   :Split file into chunks;   :Upload chunks sequentially;   while (More chunks to upload?) is (Yes)     :Upload next chunk;     if (Chunk upload successful?) then (Yes)       :Mark chunk as completed;     else (No)       :Retry chunk upload;     endif   endwhile (No)   :Reassemble chunks on server; endif :Verify file integrity; :Generate deposit confirmation; :Notify depositor of successful deposit; stop @enduml
### lmc-0012
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5714
- llm_relation_f1: 0.0000
- missing_nodes:
  - pilot is not in control (not standby)?
  - autopilot change states from standby to transition
- missing_relations:
  - pilot is not in control (not standby)? -> autopilot change states from standby to transition [yes]
- input_excerpt:
  8.	The autopilot shall change states from STANDBY to TRANSITION when the pilot is not in control (not standby).
- generated_excerpt:
  @startuml skinparam style strictuml  state "STANDBY" as STANDBY state "TRANSITION" as TRANSITION  STANDBY --> TRANSITION : [Pilot is not in control] @enduml
### us-0205
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4211
- llm_relation_f1: 0.2222
- missing_nodes:
  - get thesis paper of influential judge or legal thinker
  - gain insight into how initial scholarship start
- extra_nodes:
  - visit academic research portal
  - search for influential judge or legal thinker
  - select target individual
  - navigate to profile or bibliography
  - locate thesis paper
  - thesis paper available digitally?
  - download or view digital copy
  - submit interlibrary loan request
- missing_relations:
  - get thesis paper of influential judge or legal thinker -> gain insight into how initial scholarship start
- input_excerpt:
  As an academicresearcher, I want to the thesis paper of an influential judge or legal thinker to gain insight into how their initial scholarship got started.
- generated_excerpt:
  @startuml start :Visit academic research portal; :Search for influential judge or legal thinker; :Select target individual; :Navigate to profile or bibliography; :Locate thesis paper; if (Thesis paper available digitally?) then (Yes)   :Download or view digital copy; else (No)   :Submit interlibrary loan request;   :Wait for physical copy retrieval;   :Access physical copy; endif :Read thesis paper; :Analyze initial scholarship and early ideas; :Gain insight into origins of their legal thought; stop @enduml
### bp-0014
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1875
- relation_f1: 0.0556
- llm_element_status: success
- llm_node_f1: 0.9778
- llm_relation_f1: 0.6316
- missing_nodes:
  - select start
  - select programs
  - select businessobjects xi 3.1
  - select businessobjects enterprise
  - select businessobjects lifecycle manager
  - go to system field
  - enter cms name
  - open authentication drop-down list
- extra_nodes:
  - select start > programs > businessobjects xi 3.1 > businessobjects enterprise > businessobjects lifecycle manager
  - enter the name of the central management server (cms) in the system field
  - select the appropriate authentication method from the authentication drop-down list
  - authentication type
  - requires user name and password recognized by businessobjects enterprise system (default authentication method)
  - requires user name and password recognized by businessobjects enterprise system (requires special setup)
  - requires user name and password recognized by businessobjects enterprise system (requires special setup)
  - requires special setup (see administrator s guide)
- missing_relations:
  - select start -> select programs
  - select programs -> select businessobjects xi 3.1
  - select businessobjects xi 3.1 -> select businessobjects enterprise
  - select businessobjects enterprise -> select businessobjects lifecycle manager
  - lifecycle manager login screen appears -> go to system field
  - go to system field -> enter cms name
  - enter cms name -> enter username and password
  - enter username and password -> open authentication drop-down list
- input_excerpt:
  14.	log into the LifeCycle Manager tool.To log into the LifeCycle Manager tool, complete the following steps:1. Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager. The LifeCycle Manager login screen appears.2. In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed.3. Enter the user name and password.4. Select the appropriate authentication method from the Authentication drop-down list.The LifeCycle Manager tool supports the following authentication types:• Enterprise authentication - This authentication type requires a user name and a password that are recognize
- generated_excerpt:
  @startuml start :Select Start > Programs > BusinessObjects XI 3.1\n> BusinessObjects Enterprise > BusinessObjects LifeCycle Manager; :LifeCycle Manager login screen appears; :Enter the name of the Central Management Server (CMS)\nin the System field; :Enter the user name and password; :Select the appropriate authentication method\nfrom the Authentication drop-down list; switch (Authentication type) case (Enterprise)   :Requires user name and password recognized\nby BusinessObjects Enterprise system\n(Default authentication method); case (LDAP)   :Requires user name and password recognized\nby BusinessObjects Enterprise system\n(Requires special setup); case (Windows AD)   :Requires user name

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.

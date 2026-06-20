# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2889
- node_recall: 0.2812
- node_f1: 0.2850
- relation_precision: 0.2112
- relation_recall: 0.2216
- relation_f1: 0.2163
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7003
- llm_node_recall: 0.8350
- llm_node_f1: 0.7213
- llm_relation_precision: 0.4894
- llm_relation_recall: 0.5692
- llm_relation_f1: 0.4924

## Failure Types
- missing_activity: 20
- extra_activity: 20
- missing_or_wrong_relation: 19
- extra_or_wrong_relation: 19
- wrong_parallel: 4

## Representative Failure Cases
### us-0215
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.1905
- llm_relation_f1: 0.0000
- missing_nodes:
  - identify persons in videos and receive related information
- extra_nodes:
  - user opens the application
  - user selects or uploads a video
  - video playback starts
  - system processes video frames for person detection
  - system identifies a person in the video
  - system extracts facial features
  - person identified in database?
  - system retrieves related information
- input_excerpt:
  As a user, I want to identify persons in videos, and receive related information about them.
- generated_excerpt:
  @startuml skinparam style strictuml  title Identify Persons in Videos and Retrieve Related Information  start  :User opens the application; :User selects or uploads a video;  fork   :Video playback starts; fork again   :System processes video frames for person detection; end fork  :System identifies a person in the video; :System extracts facial features;  if (Person identified in database?) then (Yes)   :System retrieves related information;   :System displays related information to the user; else (No)   :System marks person as unknown;   :System prompts user to add new profile;      if (User adds new profile?) then (Yes)     :User inputs related information;     :System saves new profile a
### us-0038
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2000
- llm_relation_f1: 0.0952
- missing_nodes:
  - stepped zoom on map visualisations
  - get control over navigation experience
- extra_nodes:
  - data consuming user views map visualisation
  - locate zoom controls on map ui
  - click zoom in (+) button
  - request next higher zoom step
  - click zoom out (-) button
  - request next lower zoom step
  - validate requested zoom step against min/max bounds
  - is zoom step within bounds?
- missing_relations:
  - stepped zoom on map visualisations -> get control over navigation experience
- input_excerpt:
  As a Data Consuming User, I want to be able to have stepped zoom on map visualisations, So that I can have better control over the navigation experience inside a map view.
- generated_excerpt:
  @startuml skinparam style strictuml  title Stepped Zoom on Map Visualisations  start  :Data Consuming User views map visualisation;  repeat   :Locate zoom controls on map UI;      fork     :Click zoom in (+) button;     :Request next higher zoom step;   fork again     :Click zoom out (-) button;     :Request next lower zoom step;   end fork      :Validate requested zoom step against min/max bounds;      if (Is zoom step within bounds?) then (Yes)     :Apply new zoom step level;     :Render map at new zoom level;   else (No)     :Maintain current zoom level;     :Notify user of zoom limit reached;   endif  repeat while (Continue navigating map?) is (Yes)  ->No; :End map navigation session;  s
### us-0208
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4444
- llm_relation_f1: 0.2222
- missing_nodes:
  - associate a researcherid or orcid with a submission
  - avoid ambiguity between my work and others
- extra_nodes:
  - faculty member initiates submission
  - enter submission details
  - identify contributor/researcher
  - enter researcherid
  - enter orcid
  - validate researcherid/orcid format
  - valid format?
  - associate id with submission
- missing_relations:
  - associate a researcherid or orcid with a submission -> avoid ambiguity between my work and others
- input_excerpt:
  As a Cornell faculty member, I want to associate a researcherID or ORCID with a submission, so that there is no ambiguity between my work and someone else with the same name.
- generated_excerpt:
  @startuml skinparam style strictuml title Associate ResearcherID or ORCID with Submission  start  :Faculty member initiates submission;  :Enter submission details;  :Identify contributor/researcher;  fork   :Enter ResearcherID; fork again   :Enter ORCID; end fork  :Validate ResearcherID/ORCID format;  if (Valid format?) then (yes)   :Associate ID with submission;   :Confirm unique identification of contributor;   :Complete submission; else (no)   :Display validation error;   :Prompt to re-enter ID;   stop endif  stop @enduml
### lmc-0013
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.6667
- missing_nodes:
  - a failure occurs (apfail)?
  - autopilot change states from standby to maneuver
- extra_nodes:
  - standby
  - apfail?
  - maneuver
- missing_relations:
  - a failure occurs (apfail)? -> autopilot change states from standby to maneuver [yes]
- input_excerpt:
  9.	The autopilot shall change states from STANDBY to MANEUVER when a failure occurs (apfail).
- generated_excerpt:
  @startuml skinparam style strictuml start :STANDBY; if (apfail?) then (yes)   :MANEUVER; else (no) endif @enduml
### us-0025
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5714
- llm_relation_f1: 0.3333
- missing_nodes:
  - view all locations of recycling centers on a map
  - check which routes to drop off wastes
- extra_nodes:
  - user opens recycling center map view
  - app loads map interface
  - app retrieves recycling center locations from database
  - app displays all recycling center locations on the map
  - user views recycling center locations on the map
  - user selects a specific recycling center
  - app displays route options to the selected center
  - user checks routes to drop off waste
- missing_relations:
  - view all locations of recycling centers on a map -> check which routes to drop off wastes
- input_excerpt:
  As a user, I want to view all locations of recycling centers on a map, so that I can check which routes to take to drop off waste.
- generated_excerpt:
  @startuml start :User opens recycling center map view; :App loads map interface; :App retrieves recycling center locations from database; :App displays all recycling center locations on the map; :User views recycling center locations on the map; :User selects a specific recycling center; :App displays route options to the selected center; :User checks routes to drop off waste; stop @enduml
### pure-0095
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1250
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.1905
- missing_nodes:
  - refer to provided configuration
  - specify how fields are translated into warc records
  - generate errors requiring operator intervention
  - handle missing fields
  - migrate content from arc files to warc files
- extra_nodes:
  - read arc files
  - load configuration file
  - configuration specifies field translation?
  - translate arc fields into warc records
  - write warc records to output file
  - generate error for missing field(s)
  - halt migration
  - require operator intervention
- missing_relations:
  - use command arc_warc_migrate options -> refer to provided configuration
  - refer to provided configuration -> specify how fields are translated into warc records [fork]
  - refer to provided configuration -> generate errors requiring operator intervention [fork]
  - generate errors requiring operator intervention -> handle missing fields
  - specify how fields are translated into warc records -> migrate content from arc files to warc files
  - handle missing fields -> migrate content from arc files to warc files
- input_excerpt:
  Migration Tool Execution: Use the command arc_warc_migrate <ARC_FILES> <CONFIG> [options] to migrate content from ARC files to WARC files based on the provided configuration. Ensure the configuration file specifies how fields are translated into WARC records, and handle missing fields by generating errors requiring operator intervention.
- generated_excerpt:
  @startuml start :Input command: arc_warc_migrate <ARC_FILES> <CONFIG> [options]; :Read ARC files; :Load configuration file; if (Configuration specifies field translation?) then (Yes)   :Translate ARC fields into WARC records;   :Write WARC records to output file; else (No - Missing fields)   :Generate error for missing field(s);   :Halt migration;   :Require operator intervention;   stop endif :Migration complete; stop @enduml
### lmc-0047
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1667
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5882
- llm_relation_f1: 0.3333
- missing_nodes:
  - in the cockpit
  - select heading switch
  - active mode deactivates
- extra_nodes:
  - wait for pilot input
  - pilot selects heading switch?
  - activate heading hold mode
  - wait for pilot input
  - pilot deselects heading switch?
  - deactivate heading hold mode
  - heading hold remains active
- missing_relations:
  - in the cockpit -> select heading switch
  - select heading switch -> heading hold becomes active mode [case select]
  - select heading switch -> active mode deactivates [case deselect]
- input_excerpt:
  Heading Hold shall become the active mode when the pilot selects the heading switch in the cockpit and deactivate when the switch is deselected.
- generated_excerpt:
  @startuml start :Wait for pilot input; if (Pilot selects heading switch?) then (Yes)   :Activate Heading Hold mode;   :Heading Hold is active;   :Wait for pilot input;   if (Pilot deselects heading switch?) then (Yes)     :Deactivate Heading Hold mode;     stop   else (No)     :Heading Hold remains active;     note right: Loop back to wait     stop   endif else (No)   :Heading Hold remains inactive;   stop endif @enduml
### pure-0098
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1667
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7368
- llm_relation_f1: 0.3333
- missing_nodes:
  - refer to warc file content
  - summaries
  - mime-type breakdowns
  - hostname reports
  - generate reports
  - export reports in formats like xml/csv
  - apply filters
  - restrict reports by time ranges/domains
- extra_nodes:
  - generate report based on selected configurations
  - export report
- missing_relations:
  - use command warc_summary options -> refer to warc file content
  - refer to warc file content -> summaries [fork]
  - refer to warc file content -> mime-type breakdowns [fork]
  - refer to warc file content -> hostname reports [fork]
  - summaries -> generate reports
  - mime-type breakdowns -> generate reports
  - hostname reports -> generate reports
  - generate reports -> export reports in formats like xml/csv [fork]
- input_excerpt:
  Reporting Tool Execution: Use the command warc_summary <WARC_FILES> [options] to generate reports on WARC file content, such as summaries, MIME-type breakdowns, or hostname reports. Export reports in formats like XML or CSV and apply filters to restrict reports by time ranges or domains.
- generated_excerpt:
  @startuml start :Execute command `warc_summary <WARC_FILES> [options]`; fork   :Select report type:     - Summary     - MIME-type breakdown     - Hostname report; fork again   :Select export format:     - XML     - CSV; fork again   :Apply filters (optional):     - Time ranges     - Domains; end fork :Generate report based on selected configurations; :Export report; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.

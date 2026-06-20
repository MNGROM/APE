# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2816
- node_recall: 0.2957
- node_f1: 0.2885
- relation_precision: 0.2060
- relation_recall: 0.2458
- relation_f1: 0.2242
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7269
- llm_node_recall: 0.8265
- llm_node_f1: 0.7413
- llm_relation_precision: 0.5114
- llm_relation_recall: 0.5337
- llm_relation_f1: 0.4999

## Failure Types
- missing_activity: 20
- extra_activity: 20
- extra_or_wrong_relation: 20
- missing_or_wrong_relation: 19
- wrong_parallel: 5

## Representative Failure Cases
### bp-0002
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7368
- llm_relation_f1: 0.5366
- missing_nodes:
  - user authorizations are sufficient?
  - log in
  - choose modeling data warehousing workbench modeling
  - data warehousing workbench is started
  - choose info objects
  - info object tree is displayed
  - open root node context menu
  - choose create info area
- extra_nodes:
  - log onto the bi system with a user that has sufficient authorizations
  - start the data warehousing workbench in the sap menu (modeling -> data warehousing workbench modeling)
  - under modeling choose info objects (the info object tree is displayed)
  - from the context menu at the root node info objects choose create info area
  - enter a technical name and a description for the info area (the info area is displayed in the info object tree)
- missing_relations:
  - user authorizations are sufficient? -> log in [yes]
  - log in -> choose modeling data warehousing workbench modeling
  - choose modeling data warehousing workbench modeling -> data warehousing workbench is started
  - data warehousing workbench is started -> choose info objects
  - choose info objects -> info object tree is displayed
  - info object tree is displayed -> open root node context menu
  - open root node context menu -> choose create info area
  - choose create info area -> enter a technical name [fork]
- input_excerpt:
  2.	Log onto the BI system1.	Log onto the BI system with a user that has sufficient authorizations for executing the scenario.2.	Start the Data Warehousing Workbench in the SAP menu by choosing Modeling Data Warehousing Workbench: Modeling.3.	Under Modeling, choose Info  Objects. The Info  Object tree is displayed.4.	From the context menu at the root node Info Objects of the Info Object tree, choose Create Info Area.5.	On the next screen, enter a technical name and a description for the Info Area. The Info Area is displayed in the Info Object tree.6.	It is used to group your Info Objects.7.	In the context menu of the Info Area, choose Create Info Object Catalog.8.	On the next screen, enter a 
- generated_excerpt:
  @startuml start :Log onto the BI system with a user that has sufficient authorizations; :Start the Data Warehousing Workbench in the SAP menu\n(Modeling -> Data Warehousing Workbench: Modeling); :Under Modeling, choose Info Objects\n(The Info Object tree is displayed); :From the context menu at the root node Info Objects,\nchoose Create Info Area; :Enter a technical name and a description for the Info Area\n(The Info Area is displayed in the Info Object tree); note right: It is used to group your Info Objects :In the context menu of the Info Area,\nchoose Create Info Object Catalog; :Enter a technical name and description,\nand select Key Figure as the Info Object Type; :Choose Create; :Acti
### us-0116
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.4000
- missing_nodes:
  - deploy new version of app
  - it includes older version of dataset type?
  - dataset instances use type code
- extra_nodes:
  - app a creates a dataset instance
  - is dataset type x included in app a?
- missing_relations:
  - deploy new version of app -> it includes older version of dataset type?
  - it includes older version of dataset type? -> dataset instances use type code [yes]
- input_excerpt:
  As an app developer, I want to ensure that when I deploy a new version of an app that includes an older version of a dataset type deployed by another app and I expect that the dataset instances created by this app use the dataset type code included in this app.
- generated_excerpt:
  @startuml start :Deploy new version of App A (includes older version of Dataset Type X); :App A registers its included Dataset Type X (older version); :App A creates a Dataset Instance; :Runtime resolves Dataset Type code for the new instance; if (Is Dataset Type X included in App A?) then (Yes)   :Use Dataset Type X code   from App A (older version); else (No)   :Use Dataset Type X code   from other App B (newer version); endif :Dataset Instance uses the resolved Dataset Type code; stop @enduml
### lmc-0041
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.7143
- missing_nodes:
  - output u vector
  - 5x1 vector?
  - allowed
  - not allowed
- extra_nodes:
  - initialize output u vector
  - set u as a 5x1 vector
  - validate dimensions of u (5 rows 1 column)
  - is u a 5x1 vector?
  - proceed with computation
  - raise dimension mismatch error
- missing_relations:
  - output u vector -> 5x1 vector?
  - 5x1 vector? -> allowed [yes]
  - 5x1 vector? -> not allowed [no]
- input_excerpt:
  3.	The output u vector should be a 5x1 vector.
- generated_excerpt:
  @startuml start :Initialize output u vector; :Set u as a 5x1 vector; :Validate dimensions of u (5 rows, 1 column); if (Is u a 5x1 vector?) then (Yes)   :Proceed with computation; else (No)   :Raise dimension mismatch error;   stop endif stop @enduml
### us-0001
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3077
- llm_relation_f1: 0.0000
- missing_nodes:
  - make updates to sql codes
- extra_nodes:
  - broker team member identifies sql code for clarity update
  - review current sql code
  - draft sql code updates for clarity
  - validate updated sql code
  - is sql code valid?
  - commit sql code updates
  - update documentation
  - revise sql code updates
- input_excerpt:
  As a broker team member, I want to make some updates to the SQL codes for clarity.
- generated_excerpt:
  @startuml start :Broker team member identifies SQL code for clarity update; :Review current SQL code; :Draft SQL code updates for clarity; :Validate updated SQL code; if (Is SQL code valid?) then (Yes)   :Commit SQL code updates;   :Update documentation;   stop else (No)   :Revise SQL code updates;   :Review current SQL code; endif @enduml
### us-0214
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3077
- llm_relation_f1: 0.0000
- missing_nodes:
  - educate volunteer with text an image or a video
- extra_nodes:
  - zooniverse admin reviews volunteer performance
  - is volunteer struggling with the task?
  - what type of difficulty is the volunteer having?
  - recommend text-based education
  - recommend image-based education
  - is volunteer a new or passive learner?
  - recommend video-based education
  - no additional education needed
- input_excerpt:
  As a Zooniverse admin, I want to know whether I should educate a volunteer with text, an image, or a video.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Zooniverse admin reviews volunteer performance;  if (Is volunteer struggling with the task?) then (Yes)   if (What type of difficulty is the volunteer having?) then (Conceptual misunderstanding)     :Recommend text-based education;   else (Visual/spatial confusion)     :Recommend image-based education;   endif else (No)   if (Is volunteer a new or passive learner?) then (Yes)     :Recommend video-based education;   else (No)     :No additional education needed;   endif endif  stop  @enduml
### pure-0095
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1429
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.8421
- missing_nodes:
  - refer to provided configuration
  - specify how fields are translated into warc records
  - generate errors requiring operator intervention
  - handle missing fields
  - migrate content from arc files to warc files
- extra_nodes:
  - read arc files ( )
  - load configuration file ( )
  - configuration specifies field translation?
  - translate arc fields into warc records based on configuration
  - generate warc files
  - generate error for missing field translation
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
  @startuml start :Input command: arc_warc_migrate <ARC_FILES> <CONFIG> [options]; :Read ARC files (<ARC_FILES>); :Load configuration file (<CONFIG>); if (Configuration specifies field translation?) then (Yes)   :Translate ARC fields into WARC records\nbased on configuration;   :Generate WARC files; else (No - Missing fields)   :Generate error for missing field translation;   :Require operator intervention;   stop endif stop @enduml
### pure-0021
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1500
- relation_f1: 0.0889
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.5333
- missing_nodes:
  - transfer to shunting on driver s selection?
  - stationary?
  - from stand by/full supervision/partial supervision operation
  - manually select shunting
  - not allowed
  - automatic transfer?
  - speed <= supervised speed?
  - from full supervision/partial supervision operation
- extra_nodes:
  - is train stationary?
  - current operation mode?
  - driver selects shunting
  - driver selects shunting
  - driver selects shunting
  - enter shunting mode
  - manual transfer not possible
  - current operation mode?
- missing_relations:
  - transfer to shunting on driver s selection? -> stationary? [yes]
  - stationary? -> from stand by/full supervision/partial supervision operation [yes]
  - from stand by/full supervision/partial supervision operation -> manually select shunting
  - stationary? -> not allowed [no]
  - manually select shunting -> automatic transfer?
  - not allowed -> automatic transfer?
  - transfer to shunting on driver s selection? -> automatic transfer? [no]
  - automatic transfer? -> speed <= supervised speed? [yes]
- input_excerpt:
  Transfer to Shunting on driver's selection shall only be possible when stationary. It shall be possible to manually select Shunting from Stand By operation, Full Supervision operation, or Partial Supervision operation. Automatic transfer to Shunting may be from Full Supervision operation and Partial Supervision operation status at any speed lower than or equal to the supervised shunting speed based on trackside information. Before automatic transition to Shunting, ETCS shall request confirmation from the driver. Exit from Shunting shall only be possible when the train is stationary. Exit from Shunting shall take place when the driver selects exit from shunting.
- generated_excerpt:
  @startuml start  partition "Manual Transfer to Shunting" {     if (Is train stationary?) then (Yes)         switch (Current Operation Mode?)         case (Stand By)             :Driver selects Shunting;         case (Full Supervision)             :Driver selects Shunting;         case (Partial Supervision)             :Driver selects Shunting;         endswitch         :Enter Shunting Mode;     else (No)         :Manual transfer not possible;         stop     endif }  partition "Automatic Transfer to Shunting" {     switch (Current Operation Mode?)     case (Full Supervision)         if (Is speed <= supervised shunting speed\nbased on trackside info?) then (Yes)             :ETCS requests co
### bp-0009
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1538
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7619
- llm_relation_f1: 0.7619
- missing_nodes:
  - choose start programs business explorer web application designer
  - bex web is started
  - log in
  - initial screen is shown
  - click create new blank web template
  - choose new data provider
  - open data provider type dialog box
  - select query
- extra_nodes:
  - log onto the bi system
- missing_relations:
  - choose start programs business explorer web application designer -> bex web is started
  - bex web is started -> log in
  - log in -> initial screen is shown
  - initial screen is shown -> click create new blank web template
  - click create new blank web template -> choose new data provider
  - choose new data provider -> open data provider type dialog box
  - open data provider type dialog box -> select query
  - select query -> enter zd_sales_2007 as query name
- input_excerpt:
  9.	Creating Web Applications1. Start the BEx Web application by choosing Start Programs Business Explorer Web Application Designer.2. Log onto the BI system.3. In the initial screen of the Web Application Designer, click on the link Create New Blank Web Template.4. In the lower part of the layout view choose New Data Provider.5. In the dialog box for the data provider type select Query and enter the name of the query ZD_SALES_2007 in the eld following Query.6. Choose OK.7. The data provider is displayed in the lower part of the layout view in the Web Application Designer
- generated_excerpt:
  @startuml start :Start the BEx Web application by choosing Start Programs Business Explorer Web Application Designer; :Log onto the BI system; :In the initial screen of the Web Application Designer, click on the link Create New Blank Web Template; :In the lower part of the layout view choose New Data Provider; :In the dialog box for the data provider type select Query and enter the name of the query ZD_SALES_2007 in the field following Query; :Choose OK; :The data provider is displayed in the lower part of the layout view in the Web Application Designer; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.

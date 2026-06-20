# Prompt Evaluation Analysis

## Summary
- count: 30
- syntax_pass_rate: 0.9333
- infrastructure_error_rate: 0.0000
- node_precision: 0.2851
- node_recall: 0.1462
- node_f1: 0.1685
- relation_precision: 0.0485
- relation_recall: 0.0290
- relation_f1: 0.0313
- plantuml_compilation_pass_rate: 0.9333
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_activity: 30
- extra_activity: 30
- missing_or_wrong_relation: 30
- extra_or_wrong_relation: 30
- syntax_error: 2

## Representative Failure Cases
### bp-0017
- dataset: bp
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.2667
- relation_f1: 0.1538
- missing_nodes:
  - open version management systems drop-down list
  - select clearcase
  - enter details
  - clearcase map drive
  - enter mvfs s folder name
  - vob tag name
  - enter vob name
  - enter vob s folder name
- extra_nodes:
  - from the version management systems drop-down list select clearcase
- missing_relations:
  - click vms settings -> open version management systems drop-down list
  - open version management systems drop-down list -> select clearcase
  - select clearcase -> enter details
  - enter details -> clearcase map drive
  - clearcase map drive -> enter mvfs s folder name
  - enter mvfs s folder name -> vob tag name
  - vob tag name -> enter vob name
  - enter vob name -> enter vob s folder name
- input_excerpt:
  17.	set the ClearCase version management system in Unix1. In the Administration Options window, click VMS Settings.2. From the Version Management Systems drop-down list, select ClearCase.3. Enter the following details:• ClearCase Map Drive - Enter the name of the folder where the MVFSis located. By default, it is /view• VOB Tag Name - Enter the VOB name and the folder where the VOBis located. For example: VobFolder/VobName• View Storage Directory: Enter the path of the directory where the viewsare created.
- generated_excerpt:
  @startuml start :Open Administration Options window; :Click VMS Settings; :From the Version Management Systems drop-down list,\nselect ClearCase; :Enter the following details:   **ClearCase Map Drive** - Enter the name of the folder\nwhere the MVFS is located (Default: /view);   **VOB Tag Name** - Enter the VOB name and the folder\nwhere the VOB is located (e.g., VobFolder/VobName);   **View Storage Directory** - Enter the path of the\ndirectory where the views are created; stop @enduml
### bp-0013
- dataset: bp
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.2857
- relation_f1: 0.0000
- missing_nodes:
  - have existing job?
  - create a new job
  - copy existing job
  - add infoobjects
  - promote all dependencies?
  - use manage dependencies
  - open type drop-down list
  - select dependent want to promote
- extra_nodes:
  - promote a job
  - connect to the source system
  - create a new job or copy an existing job
  - create a new job or copy an existing job
  - add infoobjects to the job
  - add infoobjects to the job
  - manage dependencies (optional)
  - manage dependencies (optional)
- missing_relations:
  - connect to source system -> have existing job?
  - have existing job? -> create a new job
  - create a new job -> copy existing job
  - copy existing job -> add infoobjects
  - add infoobjects -> promote all dependencies?
  - promote all dependencies? -> use manage dependencies
  - use manage dependencies -> open type drop-down list
  - open type drop-down list -> select dependent want to promote
- input_excerpt:
  13.	promote a job when the source and the destination systems are connected, complete the following steps:1. Connect to the source system.2. Create a new job. You can also copy an existing job.3. Add infoobjects to the job you want to promote. If you do not want to promote all the dependents of the infoobjects, you can use the Manage Dependencies option to select the dependents you want to promote.Note:You can select the type of dependents you want to promote from the Type drop-down list.4. Promote the job.Promoting a job when the source system and the destination system are not connected18 To promote a job when the source and the destination systems are not connected, complete the following
- generated_excerpt:
  @startuml start :Promote a job; if (Are source and destination systems connected?) then (Yes)   :Connect to the source system;   :Create a new job or copy an existing job;   :Add infoobjects to the job;   :Manage Dependencies (optional);   note right     Select dependents to promote     Select type of dependents     from the Type drop-down list   end note;   :Promote the job; else (No)   :Connect to the source system;   :Create a new job or copy an existing job;   :Add infoobjects to the job;   :Manage Dependencies (optional);   note right     Select required dependents     Select type of dependents     from the Type drop-down list   end note;   :Export infoobjects with Output to BIAR file a
### bp-0002
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
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
  - start the data warehousing workbench (sap menu -> modeling -> data warehousing workbench modeling)
  - under modeling choose infoobjects (the infoobject tree is displayed)
  - from context menu at root node infoobjects choose create info area
  - enter technical name and description for the info area (the info area is displayed in the infoobject tree)
- missing_relations:
  - user authorizations are sufficient? -> log in
  - log in -> choose modeling data warehousing workbench modeling
  - choose modeling data warehousing workbench modeling -> data warehousing workbench is started
  - data warehousing workbench is started -> choose info objects
  - choose info objects -> info object tree is displayed
  - info object tree is displayed -> open root node context menu
  - open root node context menu -> choose create info area
  - choose create info area -> enter a technical name
- input_excerpt:
  2.	Log onto the BI system1.	Log onto the BI system with a user that has sufficient authorizations for executing the scenario.2.	Start the Data Warehousing Workbench in the SAP menu by choosing Modeling Data Warehousing Workbench: Modeling.3.	Under Modeling, choose Info  Objects. The Info  Object tree is displayed.4.	From the context menu at the root node Info Objects of the Info Object tree, choose Create Info Area.5.	On the next screen, enter a technical name and a description for the Info Area. The Info Area is displayed in the Info Object tree.6.	It is used to group your Info Objects.7.	In the context menu of the Info Area, choose Create Info Object Catalog.8.	On the next screen, enter a 
- generated_excerpt:
  @startuml start :Log onto the BI system with a user that has sufficient authorizations; :Start the Data Warehousing Workbench\n(SAP Menu -> Modeling -> Data Warehousing Workbench: Modeling); :Under Modeling, choose InfoObjects\n(The InfoObject tree is displayed); :From context menu at root node InfoObjects,\nchoose Create Info Area; :Enter technical name and description for the Info Area\n(The Info Area is displayed in the InfoObject tree); note right: Used to group your InfoObjects :In the context menu of the Info Area,\nchoose Create Info Object Catalog; :Enter technical name and description,\nselect Key Figure as Info Object Type; :Choose Create; :Activate the Info Object catalog\n(The In
### bp-0003
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - info provider tree is displayed
  - the info area is displayed
  - open context menu
  - open context menu
  - open context menu
  - choose create info cube
  - enter zd_sales as the technical name
  - enter sales overview as the description
- extra_nodes:
  - you are in the modeling functional area of the data warehousing workbench
  - choose info provider
- missing_relations:
  - info provider tree is displayed -> the info area is displayed
  - the info area is displayed -> open context menu
  - open context menu -> choose create info cube
  - choose create info cube -> enter zd_sales as the technical name
  - enter zd_sales as the technical name -> enter sales overview as the description
  - enter sales overview as the description -> select standard info cube as info provider type
  - select standard info cube as info provider type -> choose create
  - choose create -> screen for info cube editing is shown
- input_excerpt:
  3.	Creating Data sources for Master Data of Characteristic "Product"1. You are in the Modeling functional area of the Data Warehousing Workbench2. Choose Info Provider. The Info Provider tree is displayed. The Info Area created previously in the Info Object tree is also displayed in the Info Provider tree. It contains the characteristics that were dened as Info Provider and is used to group further objects.3. In the context menu of the Info Area, choose Create Info Cube.4. In the next screen, enter ZD_SALES as the technical name under Info Cube and Sales Overview as the description.5. Select Standard Info Cube as Info Provider Type and choose Create. You go to the screen for Info Cube editin
- generated_excerpt:
  @startuml start :You are in the Modeling functional area\nof the Data Warehousing Workbench; :Choose Info Provider; note right: Info Provider tree is displayed :In the context menu of the Info Area,\nchoose Create Info Cube; :Enter ZD_SALES as technical name\nand Sales Overview as description; :Select Standard Info Cube as Info Provider Type\nand choose Create; note right: Go to screen for Info Cube editing :Choose Create New Dimensions\nin context menu of folder Dimensions; :Enter Product as description\nand choose Create Another Dimension; :Enter Sales Organization as description\nand choose Continue; note right: Dimensions are inserted :Choose Info Object Catalog in toolbar; :Select Info 
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - go to data warehousing workbench
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - open data source context menu
  - open data source context menu
- extra_nodes:
  - go to the data warehousing workbench in the modeling area choose info provider
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation
  - transformation -> data source
  - data source -> open data source context menu
  - open data source context menu -> choose create info package...
  - choose create info package... -> enter description
- input_excerpt:
  7.	Loading Transaction Data1. Go to the Data Warehousing Workbench; in the Modeling area choose Info Provider. The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview.2. In the context menu of the Data source, choose Create Info Package...3. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.4. Go to the tab page Schedule and choose Start.5. To check the load process, choose Monitor in the toolbar of Info Package maintenance.6. On the next screen, select the date and choose Execute. The monitor for the load process is displayed.7. Select the load process f
- generated_excerpt:
  @startuml start :Go to the Data Warehousing Workbench;\nIn the Modeling area choose Info Provider; note right: Transformation and Data source are displayed\nin the Info Area below the Info Cube Sales Overview :In the context menu of the Data source,\nchoose Create Info Package...; :Enter a description for the Info Package\nand choose Save; note right: Info Package maintenance screen\nfor the scheduler appears :Go to the tab page Schedule\nand choose Start; :Choose Monitor in the toolbar\nof Info Package maintenance; :Select the date and choose Execute; note right: The monitor for the load process is displayed :Select the load process for your Data source\nfrom the tree at the left of the scr
### bp-0011
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - open web application
  - click on send
  - broadcasting wizard appears
  - select output format mhtml
  - system creates mhtml le
  - all components in one le
  - generate one document and broadcast it?
  - output format is suitable
- extra_nodes:
  - click on send in the web application
- missing_relations:
  - open web application -> click on send
  - click on send -> broadcasting wizard appears
  - broadcasting wizard appears -> select output format mhtml
  - select output format mhtml -> system creates mhtml le
  - system creates mhtml le -> all components in one le
  - all components in one le -> generate one document and broadcast it?
  - generate one document and broadcast it? -> output format is suitable
  - output format is suitable -> choose continue
- input_excerpt:
  11.	Broadcasting Web Applications by E-Mail1. In the Web application, click on Send. The Broadcasting Wizard appears; it guides you step-by-step through the required settings.2. Select output format MHTML. The system creates an MHTML le. All components (HTML, style sheet, pictures, and so on) of the entire HTML page are in one le. This output format is suitable if you want to generate one single document and broadcast it by e-mail or to the portal.3. Choose Continue.4. Enter the e-mail addresses of the recipients, separated with semicolons.5. Enter a subject line and text, and dene the importance of the e-mail6. Choose Execute.
- generated_excerpt:
  @startuml start :Click on Send in the Web application; note right: Broadcasting Wizard appears :Select output format MHTML; note right: Creates an MHTML file containing\nall components (HTML, style sheet,\npictures, etc.) in one single document :Choose Continue; :Enter the e-mail addresses of the recipients\n(separated with semicolons); :Enter a subject line and text; :Define the importance of the e-mail; :Choose Execute; stop @enduml
### bp-0029
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - copy the biar file
  - log in
  - open promotion jobs
  - click import biar
  - import biar file window appears
  - click browse
  - select the biar file
  - click copy
- extra_nodes:
  - copy biar file to destination system from storage device
  - log into lifecycle manager tool
  - in promotion jobs home page click import biar
- missing_relations:
  - copy the biar file -> log in
  - log in -> open promotion jobs
  - open promotion jobs -> click import biar
  - click import biar -> import biar file window appears
  - import biar file window appears -> click browse
  - click browse -> select the biar file
  - select the biar file -> click copy
  - click copy -> details appears in the new job
- input_excerpt:
  29.	Importing a Job from a BIAR File1. From the storage device, copy the BIAR file to the destination system.2. Log into the LifeCycle Manager tool.3. In the "Promotion Jobs" home page, click Import BIAR. The "Import BIAR file" window appears.4. Click Browse to select a BIAR file from the file system.5. Select the BIAR file from the file system, and click Copy. The details of the selected file appear in the "New Job" screen.6. Click Create.The job is created. You can also manage the dependencies of the job in the "Managing Dependencies" window.7. Click Promote.The "Promote - Job Name" window appears.8. Confirm the login credentials of the destination system.9. Click Promote to promote the co
- generated_excerpt:
  @startuml start :Copy BIAR file to destination system\nfrom storage device; :Log into LifeCycle Manager tool; :In "Promotion Jobs" home page,\nclick Import BIAR; note right: "Import BIAR file" window appears :Click Browse to select\na BIAR file from file system; :Select BIAR file and click Copy; note right: Details appear in "New Job" screen :Click Create; note right: Job is created fork   :Manage dependencies\nin "Managing Dependencies" window; fork again end fork :Click Promote; note right: "Promote - Job Name" window appears :Confirm login credentials\nof destination system; if (Promote or Test Promote?) then (Test Promote)   :View objects to be promoted\nand promotion status; else (Promo
### bp-0026
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0667
- relation_f1: 0.0000
- missing_nodes:
  - open the promote window
  - click mappings
  - list of crystal reports is displayed
  - select required crystal report
  - click edit crystal report properties
  - edit crystal report properties tab appears
  - modify appropriate fields
  - click apply
- extra_nodes:
  - in the promote window click mappings
  - click save or promote per your requirements
  - save
  - click save
  - promote
  - click promote
- missing_relations:
  - open the promote window -> click mappings
  - click mappings -> click crystal report mappings
  - click crystal report mappings -> list of crystal reports is displayed
  - list of crystal reports is displayed -> select required crystal report
  - select required crystal report -> click edit crystal report properties
  - click edit crystal report properties -> edit crystal report properties tab appears
  - edit crystal report properties tab appears -> modify appropriate fields
  - modify appropriate fields -> click apply
- input_excerpt:
  26.	modify the properties of a Crystal report1. In the "Promote" window, click Mappings.2. Click Crystal Report Mappings.The list of Crystal reports in the source system is displayed.3. Select the required Crystal report, and click Edit Crystal Report Properties. The "Edit Crystal Report Properties" tab appears, as shown in the following figure: This tab displays the list of properties and their values.4. Modify the appropriate fields, and click Apply. The Crystal Report Mappings tab appears.Note:• If you edit a Crystal report in the source system, the following message is displayed beside the Crystal report: edited• A Crystal Report created using Universes cannot be mapped in the Crystal Re
- generated_excerpt:
  @startuml skinparam style strictuml skinparam NoteFontColor black skinparam NoteBackgroundColor white  start  :In the "Promote" window, click Mappings;  :Click Crystal Report Mappings; note right: The list of Crystal reports\nin the source system is displayed.  :Select the required Crystal report, and click Edit Crystal Report Properties; note right: The "Edit Crystal Report Properties" tab appears.\nThis tab displays the list of\nproperties and their values.  :Modify the appropriate fields, and click Apply; note right   The Crystal Report Mappings tab appears.   ----   **Notes:**   * If you edit a Crystal report in the     source system, the following message     is displayed beside the Cry

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.

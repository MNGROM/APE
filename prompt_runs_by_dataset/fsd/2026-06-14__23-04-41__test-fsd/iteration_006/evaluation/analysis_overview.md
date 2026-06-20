# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2672
- node_recall: 0.4077
- node_f1: 0.3229
- relation_precision: 0.2137
- relation_recall: 0.3288
- relation_f1: 0.2590
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7776
- llm_node_recall: 0.8749
- llm_node_f1: 0.7951
- llm_relation_precision: 0.6246
- llm_relation_recall: 0.6902
- llm_relation_f1: 0.6225

## Failure Types
- extra_activity: 20
- extra_or_wrong_relation: 19
- missing_activity: 18
- missing_or_wrong_relation: 18
- wrong_parallel: 2
- wrong_loop: 1

## Representative Failure Cases
### lmc-0035
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.7692
- missing_nodes:
  - input any value
  - maximum value of nn output z <= 1.1?
  - allowed
  - not allowed
- extra_nodes:
  - receive input values for nn
  - compute nn output z
  - z <= 1.1?
  - accept z
  - clamp/reject z (enforce z <= 1.1)
- missing_relations:
  - input any value -> maximum value of nn output z <= 1.1?
  - maximum value of nn output z <= 1.1? -> allowed [yes]
  - maximum value of nn output z <= 1.1? -> not allowed [no]
- input_excerpt:
  1.	The maximum value of the NN output, z, shall always be less than or equal to 1.1, regardless of the input values.
- generated_excerpt:
  @startuml start :Receive input values for NN; :Compute NN output z; if (z <= 1.1?) then (Yes)   :Accept z; else (No)   :Clamp/Reject z\n(Enforce z <= 1.1); endif stop @enduml
### pure-0027
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7500
- llm_relation_f1: 0.3333
- missing_nodes:
  - get correlator-backend network interface
  - receive incoming data packets
- extra_nodes:
  - receive incoming data packets from correlator to backend network interface
- missing_relations:
  - get correlator-backend network interface -> receive incoming data packets
- input_excerpt:
  Data Receive – The BE shall receive incoming data packets from the Correlator to Backend network interface. This network is a part of the BE System.
- generated_excerpt:
  @startuml start :Receive incoming data packets from Correlator to Backend network interface; note right: Network is part of the BE System :Process received data packets; stop @enduml
### bp-0002
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8837
- llm_relation_f1: 0.9455
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
  - under modeling choose info objects (the info object tree is displayed)
  - from the context menu at the root node info objects choose create info area
  - enter a technical name and a description for the info area
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
  @startuml start :Log onto the BI system with a user that has sufficient authorizations; :Start the Data Warehousing Workbench\n(SAP Menu -> Modeling -> Data Warehousing Workbench: Modeling); :Under Modeling, choose Info Objects\n(The Info Object tree is displayed); :From the context menu at the root node Info Objects,\nchoose Create Info Area; :Enter a technical name and a description for the Info Area; note right: The Info Area is displayed in the Info Object tree.\nIt is used to group your Info Objects. :In the context menu of the Info Area,\nchoose Create Info Object Catalog; :Enter a technical name and description,\nand select Key Figure as the Info Object Type; :Choose Create; :Activate
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
  @startuml skinparam style strictuml start :STANDBY; if (apfail?) then (yes)   :MANEUVER; else (no) endif stop @enduml
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.1176
- llm_element_status: success
- llm_node_f1: 0.6842
- llm_relation_f1: 0.6486
- missing_nodes:
  - sort revenue data
  - click arrows in revenue eld?
  - sort increasing or decreasing
  - click alternative mouse button
  - open context menu
  - choose sort increasing or sort decreasing
  - internet channel is the greatest
  - analyze differences for months?
- extra_nodes:
  - click arrows in the revenue field to sort data (increasing/decreasing)
  - right-click revenue and choose sort (increasing/decreasing) from context menu
  - observe greatest revenue is from internet channel
  - select 08.2007 in calendar year/month dropdown
  - select 07.2007 in calendar year/month dropdown
  - observe internet revenue increased greatly (successful campaign)
  - filter data back to september by selecting 09.2007 in dropdown
  - right-click subtotal of internet channel (567.308 05)
- missing_relations:
  - sort revenue data -> click arrows in revenue eld?
  - click arrows in revenue eld? -> sort increasing or decreasing [yes]
  - click arrows in revenue eld? -> click alternative mouse button [no]
  - click alternative mouse button -> open context menu
  - open context menu -> choose sort increasing or sort decreasing
  - sort increasing or decreasing -> internet channel is the greatest
  - choose sort increasing or sort decreasing -> internet channel is the greatest
  - internet channel is the greatest -> analyze differences for months?
- input_excerpt:
  10.	Analyzing Data in the Web Application1. Since you are interested in the revenue, you want to sort the revenue data.2. Click on the arrows in the Revenue eld to sort the revenue data in increasing or decreasing order.3. You can also sort the revenue by clicking the alternative mouse button on Revenue and choosing Sort Sort Increasing or Sort Decreasing in the context menu. You see that the greatest revenue is obtained with the distribution channel Internet.4. To see the differences in the revenue data for the months July, August and September, select rst 08.2007 and then 07.2007 in the dropdown box Calendar Year/Month. You see that the revenue data for the distribution channel Internet in
- generated_excerpt:
  @startuml start :Click arrows in the Revenue field to sort data (Increasing/Decreasing); :Right-click Revenue and choose Sort (Increasing/Decreasing) from context menu; :Observe greatest revenue is from Internet channel; :Select 08.2007 in Calendar Year/Month dropdown; :Select 07.2007 in Calendar Year/Month dropdown; :Observe Internet revenue increased greatly (successful campaign); :Filter data back to September by selecting 09.2007 in dropdown; :Right-click subtotal of Internet channel (567.308,05); :Select Documents > Create New Comment from context menu; :Enter name and description for the document; :Enter text and choose Save; stop @enduml
### us-0101
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1538
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3158
- llm_relation_f1: 0.1053
- extra_nodes:
  - access repository management panel
  - select user groups section
  - click create new group
  - enter group name and description
  - configure group permissions
  - more users to assign?
  - review group details and permissions
  - confirm and save group?
- input_excerpt:
  As a collection curator, I want to create groups of users to manage permissions in the repository in an easy way.
- generated_excerpt:
  @startuml skinparam style strictuml  title Activity Diagram: Create User Groups for Permission Management  start  :Access repository management panel;  :Select "User Groups" section;  :Click "Create New Group";  :Enter group name and description;  :Configure group permissions;  repeat :Assign users to the group; repeat while (More users to assign?) is (Yes) -> No;  :Review group details and permissions;  if (Confirm and save group?) then (Yes)   :Save user group;   :Group successfully created;   :Manage repository permissions via group; else (No)   :Edit or discard group;   stop endif  stop @enduml
### pure-0054
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1765
- relation_f1: 0.0526
- llm_element_status: success
- llm_node_f1: 0.9048
- llm_relation_f1: 0.6977
- missing_nodes:
  - donor/primary contact has valid donation number
  - arrive at receiving dock
  - see view acquisitions
  - locate donation request
  - see add item to inventory
  - enter information
  - way to add item
  - clone an existing item
- extra_nodes:
  - donor or primary contact arrives at receiving dock with a valid donation number
  - receiving associate locates donation request in the system (see view acquisitions)
  - receiving associate enters information about each donated item into the donation request (see add item to inventory)
  - a new item can be added to the list by cloning an existing item
  - an item can be removed by setting the received quantity to zero
  - receiving associate prints a donation receipt
  - receiving associate optionally writes information to the receipt by hand such as condition
  - receiving associate prints item tags for unique and stock items (see add item to inventory)
- missing_relations:
  - arrive at receiving dock -> see view acquisitions
  - see view acquisitions -> locate donation request
  - locate donation request -> display donation request information
  - display donation request information -> see add item to inventory
  - see add item to inventory -> enter information
  - enter information -> add new item?
  - add new item? -> way to add item [yes]
  - way to add item -> clone an existing item [case clone]
- input_excerpt:
  1. Donor or Primary Contact arrives at receiving dock with a valid donation number 2. Receiving Associate locates donation request in the system (see View Acquisitions) 3. System displays donation request information 4. Receiving Associate enters information about each donated item into the donation request (see Add Item to Inventory) 4.1. A new item can be added to the list by cloning an existing item 4.2. A new item can be added by clicking the Add Item button 4.3. An item can be removed by setting the received quantity to zero 5. Receiving Associate prints a donation receipt 6. Receiving Associate optionally writes information to the receipt by hand such as condition 7. Donation receipt i
- generated_excerpt:
  @startuml start :Donor or Primary Contact arrives at receiving dock\nwith a valid donation number; :Receiving Associate locates donation request\nin the system (see View Acquisitions); :System displays donation request information; :Receiving Associate enters information about\neach donated item into the donation request\n(see Add Item to Inventory); fork   :A new item can be added to the list\nby cloning an existing item; fork again   :A new item can be added by clicking\nthe Add Item button; fork again   :An item can be removed by setting\nthe received quantity to zero; end fork :Receiving Associate prints a donation receipt; :Receiving Associate optionally writes\ninformation to the recei
### bp-0014
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1875
- relation_f1: 0.0556
- llm_element_status: success
- llm_node_f1: 0.8636
- llm_relation_f1: 0.6829
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
  - use enterprise authentication (requires user name and password recognized by businessobjects enterprise system) (default method)
  - use ldap authentication (requires user name and password recognized by businessobjects enterprise system) (requires special setup)
  - use windows ad authentication (requires user name and password recognized by businessobjects enterprise system) (requires special setup)
  - use other third-party authentication (requires special setup)
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
  @startuml start :Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager; :The LifeCycle Manager login screen appears; :Enter the name of the Central Management Server (CMS) in the System field; :Enter the user name and password; :Select the appropriate authentication method from the Authentication drop-down list; switch (Authentication type) case (Enterprise)   :Use Enterprise authentication\n(requires user name and password\nrecognized by BusinessObjects Enterprise system)\n(Default method); case (LDAP)   :Use LDAP authentication\n(requires user name and password\nrecognized by BusinessObjects Enterprise system)\n(Requires special s

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.

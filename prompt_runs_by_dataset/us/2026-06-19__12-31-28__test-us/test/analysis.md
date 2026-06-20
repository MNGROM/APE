# Prompt Evaluation Analysis

## Summary
- count: 30
- syntax_pass_rate: 0.9667
- infrastructure_error_rate: 0.0000
- node_precision: 0.4749
- node_recall: 0.6583
- node_f1: 0.5518
- relation_precision: 0.3050
- relation_recall: 0.4000
- relation_f1: 0.3461
- plantuml_compilation_pass_rate: 0.9667
- llm_element_evaluated: 30.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7512
- llm_node_recall: 0.9056
- llm_node_f1: 0.8053
- llm_relation_precision: 0.5387
- llm_relation_recall: 0.6517
- llm_relation_f1: 0.5734

## Failure Types
- extra_activity: 24
- extra_or_wrong_relation: 22
- missing_or_wrong_relation: 19
- missing_activity: 19
- wrong_parallel: 4
- syntax_error: 1

## Representative Failure Cases
### us-0007
- dataset: us
- failure_types: syntax_error, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.3333
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6000
- llm_relation_f1: 0.2000
- extra_nodes:
  - view financial assistance data
  - daily timer triggered?
  - display updated financial assistance data
  - continue viewing?
- input_excerpt:
  As a website user, I want to see updated financial assistance data daily.
- generated_excerpt:
  @startuml start :View financial assistance data; repeat :Update financial assistance data; repeat while (Daily timer triggered?) is (no) ->yes; :Display updated financial assistance data; repeat while (Continue viewing?) is (yes) ->no; stop @enduml
### us-0006
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4000
- llm_relation_f1: 0.0000
- missing_nodes:
  - accept zero and blank for non-loan records
- extra_nodes:
  - process fabs record
  - is record a non-loan?
  - accept zero
  - accept blank
  - apply standard validation rules
- input_excerpt:
  As an agency user, I want the FABS validation rules to accept zero and blank for non-loan records.
- generated_excerpt:
  @startuml start :Process FABS record; if (Is record a non-loan?) then (yes)   fork     :Accept zero;   fork again     :Accept blank;   end fork else (no)   :Apply standard validation rules; endif stop @enduml
### us-0019
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - issue a notice of violation
  - provide formal communication
- extra_nodes:
  - enforcement staff member issues notice of violation
  - provide formal communication to responsible party
- missing_relations:
  - issue a notice of violation -> provide formal communication
- input_excerpt:
  As an Enforcement Staff member, I want to Issue a Notice of Violation, so that I can provide formal communication to the responsible party.
- generated_excerpt:
  @startuml start :Enforcement Staff member issues Notice of Violation; :Provide formal communication to responsible party; stop @enduml
### us-0005
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.2222
- llm_element_status: success
- llm_node_f1: 0.2857
- llm_relation_f1: 0.1538
- missing_nodes:
  - manage d files generation requests
  - avoid performance issues caused by duplicate requests
- extra_nodes:
  - receive d files generation request
  - check cache for existing d files
  - cache hit?
  - retrieve d files from cache
  - generate d files
  - return d files
- missing_relations:
  - cache d files generation requests -> avoid performance issues caused by duplicate requests
- input_excerpt:
  As a Developer, I want D Files generation requests to be managed and cached, so that duplicate requests do not cause performance issues.
- generated_excerpt:
  @startuml start :Receive D Files generation request; :Check cache for existing D Files; if (Cache hit?) then (Yes)   :Retrieve D Files from cache; else (No)   :Generate D Files;   :Cache generated D Files; endif :Return D Files; stop @enduml
### us-0015
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3636
- llm_relation_f1: 0.1818
- missing_nodes:
  - meet service level and quality requirements
- extra_nodes:
  - view inspector workloads
  - assess service level requirements
  - assess quality requirements
  - workload adjustment needed?
  - reassign inspections
- missing_relations:
  - manage inspector workload -> meet service level and quality requirements
- input_excerpt:
  As an Inspection Supervisor, I want to Manage Inspector Workload, so that I can meet service level and quality requirements.
- generated_excerpt:
  @startuml start :Manage Inspector Workload; :View Inspector Workloads; :Assess Service Level Requirements; :Assess Quality Requirements; if (Workload Adjustment Needed?) then (Yes)   :Reassign Inspections; else (No) endif stop @enduml
### us-0024
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.9091
- llm_relation_f1: 0.5455
- missing_nodes:
  - use website
  - delete content
- extra_nodes:
  - access website
  - choose action
  - delete stuff
- missing_relations:
  - use website -> upload content [fork]
  - use website -> delete content [fork]
  - upload content -> use website [merge]
  - delete content -> use website [merge]
- input_excerpt:
  As a company, I want to have a website that is easy to use, so that I can upload or delete stuff step by step.
- generated_excerpt:
  @startuml start :Access website; switch (Choose action) case (Upload)   :Upload stuff; case (Delete)   :Delete stuff; endswitch stop @enduml
### us-0012
- dataset: us
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.4000
- llm_element_status: success
- llm_node_f1: 0.7273
- llm_relation_f1: 0.4000
- missing_nodes:
  - validate when application is complete and eligible
- extra_nodes:
  - validate application completeness
  - is the application complete?
  - mark application as eligible for further technical review
  - mark application as incomplete
- input_excerpt:
  As a Staff member, I want to Perform a Completeness Review, so that I can validate when an application is complete and eligible for further technical review.
- generated_excerpt:
  @startuml start :Perform a Completeness Review; :Validate application completeness; if (Is the application complete?) then (Yes) :Mark application as eligible for further technical review; else (No) :Mark application as incomplete; endif stop @enduml
### us-0011
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6000
- llm_relation_f1: 0.0000
- missing_nodes:
  - log on to customer portal
  - perform transactions that first require user authentication
- extra_nodes:
  - enter user account details
  - submit account creation request
- missing_relations:
  - create a customer portal user account -> log on to customer portal
  - log on to customer portal -> perform transactions that first require user authentication
- input_excerpt:
  As a Customer, I want to Create a Customer Portal User Account, so that I can log on to the Customer Portal and perform transactions that first require user authentication.
- generated_excerpt:
  @startuml start :Enter user account details; :Submit account creation request; :Create Customer Portal User Account; stop @enduml
### us-0014
- dataset: us
- failure_types: extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3636
- relation_f1: 0.1667
- llm_element_status: success
- llm_node_f1: 0.5333
- llm_relation_f1: 0.2500
- extra_nodes:
  - select management action
  - enter hearing details
  - save hearing to calendar
  - select existing hearing
  - modify hearing details
  - update hearing on calendar
  - remove hearing from calendar
- input_excerpt:
  As a Staff member, I want to Manage Hearing Calendars, so that I can track hearing-related activities and due dates.
- generated_excerpt:
  @startuml start :Access Hearing Calendar Management; switch (Select Management Action) case (Add Hearing)   :Enter hearing details;   :Save hearing to calendar; case (Edit Hearing)   :Select existing hearing;   :Modify hearing details;   :Update hearing on calendar; case (Delete Hearing)   :Select existing hearing;   :Remove hearing from calendar; endswitch :Track hearing-related activities and due dates; stop @enduml
### us-0003
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 1.0000
- missing_nodes:
  - design a schedule from ui sme
- extra_nodes:
  - access ui sme
  - design schedule
- missing_relations:
  - design a schedule from ui sme -> get timeline of the ui improvements
- input_excerpt:
  As an Owner, I want to design a schedule from the UI SME, so that I know the potential timeline of the UI improvements wanted.
- generated_excerpt:
  @startuml start :Access UI SME; :Design schedule; :View potential timeline of UI improvements; stop @enduml
### us-0008
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.8571
- missing_nodes:
  - give advanced notice to ensure buy-in
- extra_nodes:
  - give testers advanced notice
  - ensure buy-in
- missing_relations:
  - schedule user testing -> give advanced notice to ensure buy-in
- input_excerpt:
  As a UI designer, I want to schedule user testing, so that I can give the testers advanced notice to ensure buy-in.
- generated_excerpt:
  @startuml start :Schedule user testing; :Give testers advanced notice; :Ensure buy-in; stop @enduml
### us-0017
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.2857
- missing_nodes:
  - receive work
- extra_nodes:
  - select appropriate inspector
  - send work to inspector
- missing_relations:
  - assign inspections -> receive work
- input_excerpt:
  As an Inspection Staff Supervisor, I want to Assign Inspections, so that I can make sure the appropriate Inspector receives the work.
- generated_excerpt:
  @startuml start :Assign Inspections; :Select appropriate Inspector; :Send work to Inspector; stop @enduml
### us-0030
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.2857
- missing_nodes:
  - integrate api and implement certain features in own application
- extra_nodes:
  - integrate api
  - implement features in ios application
- missing_relations:
  - access an api from the website -> integrate api and implement certain features in own application
- input_excerpt:
  As a developer, I want to access an API from the website, so that I can integrate it and implement certain features in my own iOS application.
- generated_excerpt:
  @startuml start :Access API from website; :Integrate API; :Implement features in iOS application; stop @enduml
### us-0022
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.4000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.8571
- missing_nodes:
  - access user stats and schedules
  - adjust time
- extra_nodes:
  - access user stats
  - access schedules
  - adjust hours
  - upgrade capacity
- missing_relations:
  - access user stats and schedules -> adjust time [fork]
  - access user stats and schedules -> upgrade equipment and capacity [fork]
- input_excerpt:
  As a recyclingfacility representative, I want to have access to user stats and schedules, so that I can adjust my hours and/or upgrade equipment and capacity in order to be able to accomodate larger amounts of recyclable materials.
- generated_excerpt:
  @startuml start :Access user stats; :Access schedules; fork   :Adjust hours; fork again   :Upgrade equipment;   :Upgrade capacity; end fork :Accommodate larger amounts of recyclable materials; stop @enduml
### us-0001
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7500
- llm_relation_f1: 0.3333
- extra_nodes:
  - log in as broker team member
  - identify sql codes for clarity updates
- input_excerpt:
  As a broker team member, I want to make some updates to the SQL codes for clarity.
- generated_excerpt:
  @startuml start :Log in as broker team member; :Identify SQL codes for clarity updates; :Make updates to the SQL codes; stop @enduml
### us-0028
- dataset: us
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - design website
- extra_nodes:
  - easily design website
- input_excerpt:
  As a developer, I want to use bootstrap in the process of developing, so that I can easily design my website.
- generated_excerpt:
  @startuml start :Use bootstrap in the process of developing; :Easily design website; stop @enduml
### us-0029
- dataset: us
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - process cases the first time
- extra_nodes:
  - process case
- input_excerpt:
  As an employee, I want to get quick notifications, so that I can process cases the first time.
- generated_excerpt:
  @startuml start :Receive quick notification; :Process case; stop @enduml
### us-0004
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5455
- llm_relation_f1: 0.2000
- extra_nodes:
  - identify fields
  - retain zero-padding
  - apply zero-padding to field
- missing_relations:
  - use zero-padded fields -> justify padding
- input_excerpt:
  As an owner, I only want zero-padded fields, so that I can justify padding.
- generated_excerpt:
  @startuml start :Identify fields; if (Is field zero-padded?) then (Yes)   :Retain zero-padding; else (No)   :Apply zero-padding to field; endif :Justify padding; stop @enduml
### us-0013
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.9091
- llm_relation_f1: 0.1818
- missing_nodes:
  - receive result of preapplication assistance
- extra_nodes:
  - assistance type
  - receive information response
- missing_relations:
  - request preapplication assistance -> receive a response to a request for a meeting [fork]
  - request preapplication assistance -> receive result of preapplication assistance [fork]
  - receive a response to a request for a meeting -> receive result of preapplication assistance [merge]
- input_excerpt:
  As an Applicant, I want to Request PreApplication Assistance, so that I can receive a response to a request for a meeting or information that is a result of the preapplication assistance.
- generated_excerpt:
  @startuml start :Request PreApplication Assistance; switch (Assistance Type) case (Meeting)   :Receive Meeting Response; case (Information)   :Receive Information Response; endswitch stop @enduml
### us-0009
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.5714
- missing_nodes:
  - move on to round 2 landing page edits
- extra_nodes:
  - choose landing page type
  - landing page type
  - move to round 2
- missing_relations:
  - move on to round 2 landing page edits -> dabs landing page edits [fork]
  - move on to round 2 landing page edits -> fabs landing page edits [fork]
  - dabs landing page edits -> get approvals from leadership [merge]
  - fabs landing page edits -> get approvals from leadership [merge]
- input_excerpt:
  As a UI designer, I want to move on to round 2 of DABS or FABS landing page edits, so that I can get approvals from leadership.
- generated_excerpt:
  @startuml start :Choose landing page type; switch (Landing page type) case (DABS)   :Edit DABS landing page; case (FABS)   :Edit FABS landing page; endswitch :Move to round 2; :Get approvals from leadership; stop @enduml
### us-0020
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.5000
- missing_nodes:
  - publish report according to business rules
- extra_nodes:
  - publish the report
- missing_relations:
  - develop a staff report -> publish report according to business rules
  - publish report according to business rules -> distribute report according to business rules
- input_excerpt:
  As a Staff member, I want to Develop a Staff Report, so that I can publish and distribute the report according to business rules.
- generated_excerpt:
  @startuml start :Develop a Staff Report; :Publish the report; fork     :Distribute the report according to business rules; end fork stop @enduml
### us-0026
- dataset: us
- failure_types: missing_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.4000
- missing_nodes:
  - use website conveniently
- missing_relations:
  - select flexible pick-up time -> use website conveniently
- input_excerpt:
  As a user, I want to have a flexible pick up time, so that I can more conveniently use the website.
- generated_excerpt:
  @startuml start :Select flexible pick up time; stop @enduml
### us-0027
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.5000
- extra_nodes:
  - analyze schedule for availability
  - display recommendations
- missing_relations:
  - upload week s schedule -> get recommendations for recycling centers
- input_excerpt:
  As a user, I want to upload my week's schedule, so that I can get recommendations for recycling centers that best fit my availability.
- generated_excerpt:
  @startuml start :Upload week's schedule; :Analyze schedule for availability; :Generate recycling center recommendations; :Display recommendations; stop @enduml
### us-0018
- dataset: us
- failure_types: extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.5000
- extra_nodes:
  - login as development staff member
  - select request to issue development-related permit
- input_excerpt:
  As a Development Staff member, I want to Issue a Development-related Permit, so that I can grant the request to the Applicant to begin work
- generated_excerpt:
  @startuml start :Login as Development Staff member; :Select request to issue Development-related Permit; :Issue Development-related Permit; :Grant request to Applicant to begin work; stop @enduml
### us-0021
- dataset: us
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 1.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - determine considered facility
- extra_nodes:
  - determine which facilities to consider
- input_excerpt:
  As a user, I want to be able to enter my zip code and get a list of nearby recycling facilities, so that I can determine which ones I should consider.
- generated_excerpt:
  @startuml start :Enter zip code; :Get list of nearby recycling facilities; :Determine which facilities to consider; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.

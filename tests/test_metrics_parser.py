import unittest

from llm_element_metrics import CompilationResult, LLMElementMetrics, PRF
from metrics import EvaluationRecord, MetricBundle, SyntaxResult, extract_activity_graph, summarize_records


class MetricsParserTest(unittest.TestCase):
    def test_fork_end_matches_end_fork(self) -> None:
        fork_end = """@startuml
start
:A;
fork
:B;
fork again
:C;
fork end
:D;
stop
@enduml"""
        end_fork = fork_end.replace("fork end", "end fork")

        self.assertEqual(extract_activity_graph(fork_end), extract_activity_graph(end_fork))
        self.assertEqual(
            extract_activity_graph(fork_end).relations,
            ["a -> b [fork]", "a -> c [fork]", "b -> d", "c -> d"],
        )

    def test_inline_note_does_not_create_node(self) -> None:
        code = """@startuml
start
:A;
note right: explanatory note
:B;
stop
@enduml"""

        graph = extract_activity_graph(code)

        self.assertEqual(graph.nodes, ["a", "b"])
        self.assertEqual(graph.relations, ["a -> b"])

    def test_styled_arrow_does_not_pollute_source_or_target(self) -> None:
        code = """@startuml
start
:A;
A -[bold]-> (No);
(No) -[#red,dashed]-> B : ok;
:Done;
stop
@enduml"""

        graph = extract_activity_graph(code)

        self.assertNotIn("a - bold", graph.nodes)
        self.assertEqual(graph.nodes, ["a", "(no)", "b", "done"])
        self.assertEqual(
            graph.relations,
            ["a -> (no) [transition]", "(no) -> b [ok]", "b -> done"],
        )

    def test_shorthand_arrow_labels_next_relation(self) -> None:
        code = """@startuml
start
:A;
if(X?) then(yes)
:B;
else(no)
:C;
endif
->No;
:D;
stop
@enduml"""

        graph = extract_activity_graph(code)

        self.assertIn("b -> d [no]", graph.relations)
        self.assertIn("c -> d [no]", graph.relations)
        self.assertNotIn("no", graph.nodes)

    def test_repeat_exit_arrow_relabels_next_relation(self) -> None:
        code = """@startuml
start
repeat
:Poll;
repeat while(Ready?) is(no)
->yes;
:Finish;
stop
@enduml"""

        graph = extract_activity_graph(code)

        self.assertIn("ready? -> finish [yes]", graph.relations)

    def test_nested_if_fork_smoke(self) -> None:
        code = """@startuml
start
:A;
if(X?) then(yes)
fork
:B;
fork again
:C;
end fork
else(no)
:D;
endif
:E;
stop
@enduml"""

        graph = extract_activity_graph(code)

        self.assertIn("x? -> b [yes]", graph.relations)
        self.assertIn("x? -> c [yes]", graph.relations)
        self.assertIn("d -> e", graph.relations)

    def test_duplicate_labels_are_deduped_before_metrics(self) -> None:
        code = """@startuml
start
if(A?) then(no)
:Abort Cycle;
else(yes)
  if(B?) then(no)
  :Abort Cycle;
  else(yes)
  endif
endif
fork
:Monitor;
fork again
:Log;
end fork
stop
@enduml"""

        graph = extract_activity_graph(code)

        self.assertEqual(graph.nodes.count("abort cycle"), 1)
        self.assertEqual(graph.relations.count("abort cycle -> monitor [fork]"), 1)
        self.assertEqual(graph.relations.count("abort cycle -> log [fork]"), 1)

    def test_summary_excludes_syntax_pass_rate(self) -> None:
        metric = MetricBundle(precision=1.0, recall=1.0, f1=1.0, missing=[], extra=[])
        zero = PRF(precision=0.0, recall=0.0, f1=0.0)
        record = EvaluationRecord(
            dataset="demo",
            case_id="demo-1",
            input_requirement="Do work",
            gold_plantuml="@startuml\n@enduml",
            generated_plantuml="@startuml\n@enduml",
            syntax=SyntaxResult(passed=True, errors=[]),
            node_metrics=metric,
            relation_metrics=metric,
            plantuml_compilation=CompilationResult(passed=True, errors=[]),
            llm_element_metrics=LLMElementMetrics(
                enabled=False,
                status="disabled",
                node_metrics=zero,
                relation_metrics=zero,
                gt_elements={},
                pred_elements={},
                matching={},
                counts={},
            ),
            failure_types=[],
        )

        summary = summarize_records([record])

        self.assertNotIn("syntax_pass_rate", summary)
        self.assertEqual(summary["plantuml_compilation_pass_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()

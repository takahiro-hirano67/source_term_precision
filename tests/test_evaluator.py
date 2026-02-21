from source_term_precision import GroundingEvaluator

# Initialize the evaluator (Loads Sudachi dictionary)
# 評価器の初期化（Sudachi辞書がロードされます）
evaluator = GroundingEvaluator()

source_text = """
本発明は、半導体記憶装置の製造方法に関する。
特に、メモリセルアレイと周辺回路を同一基板上に形成する工程において、
熱処理温度を制御することで欠陥を低減する技術である。
"""

llm_output = """
### 概要
- この文書は半導体記憶装置の製造プロセスについて説明しています。
- シリコンウェハーの熱処理を行うことで、メモリセルの速度を10%向上させます。

除外語テスト: アイデア
"""

# Run evaluation
result = evaluator.evaluate(
    llm_output=llm_output,
    source_text=source_text,
    exact_excludes={"アイデア"}, # 除外語指定（完全一致）
    partial_excludes={"文書"} # 除外語指定（部分一致※）
)

print(f"Score (P_src): {result.score:.2f}")
print(f"Found Words: {result.found_words}")
print(f"Missing Words (Potential Hallucinations): {result.missing_words}")
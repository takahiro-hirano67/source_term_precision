# Source Term Precision

[PyPI](https://pypi.org/project/source-term-precision/)

A Python package to evaluate LLM hallucination and grounding for Japanese text, based on Source-based Term Precision ($P_{src}$).

This metric calculates the ratio of compound terms in the LLM-generated text that are explicitly present in the provided source text. It treats the input source text as the Single Source of Truth (SSoT) to act as a primary filter against plausible but fabricated terminology (hallucinations), especially in strict domains like patent analysis.

---

本パッケージは、LLM（大規模言語モデル）が生成した日本語テキストのハルシネーションを評価・検知するための評価指標「原典適合率（ $P_{src}$ ）」を算出するPythonライブラリです。入力原文を唯一の情報源（SSoT）とみなし、原文に存在しない用語の出現をペナルティ化することで、専門家のファクトチェック前の一次フィルタとして機能します。

<img width="1218" height="689" alt="image" src="https://github.com/user-attachments/assets/304a06a1-71ad-4488-a046-0f01e9688ed0" />

## Installation

```bash
pip install source_term_precision
```

## Quick Start

```python
from source_term_precision import GroundingEvaluator

# 評価器の初期化（初回呼び出し時にSudachi辞書をロードします）
evaluator = GroundingEvaluator()

# LLMが参照した原文（Single Source of Truth）
source_text = """
本発明は、半導体記憶装置の製造方法に関する。
特に、メモリセルアレイと周辺回路を同一基板上に形成する工程において、
熱処理温度を制御することで欠陥を低減する技術である。
"""

# LLMによって生成されたテキスト
llm_output = """
### 概要
- この文書は半導体記憶装置の製造プロセスについて説明しています。
- シリコンウェハーの熱処理を行うことで、メモリセルの速度を10%向上させます。

除外語テスト: アイデア
"""

# 評価の実行
result = evaluator.evaluate(
    llm_output=llm_output,
    source_text=source_text,
    exact_excludes={"アイデア"},   # 除外語指定（完全一致）
    partial_excludes={"文書"}      # 除外語指定（部分一致 ※）
)

print(f"Score (P_src): {result.score:.2f}")
print(f"Found Words: {result.found_words}")
print(f"Missing Words (Potential Hallucinations): {result.missing_words}")

# --- Output ---
# Score (P_src): 0.40
# Found Words: ['半導体記憶装置', '熱処理', 'こと', 'メモリセル']
# Missing Words (Potential Hallucinations): ['製造プロセス', '説明', 'シリコンウェハー', '速度', '10%向上', '除外語テスト']
```

> **Note:** `partial_excludes`（部分一致での除外）は、意図しない複合語まで除外してしまう可能性があるため、タスクの出力形式に合わせて慎重に指定してください。

## 処理のイメージ

<img width="1079" height="340" alt="image" src="https://github.com/user-attachments/assets/a79512f3-0f54-4208-9724-c0e40d5dc50f" />

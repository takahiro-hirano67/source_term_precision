import re
from dataclasses import dataclass
from typing import List, Optional, Set

from sudachipy import dictionary, tokenizer


@dataclass
class GroundingResult:
    """評価結果を格納するデータクラス"""

    score: float
    found_words: List[str]
    missing_words: List[str]


class GroundingEvaluator:
    """グラウンディングスコア（原典適合率）を計算する評価器"""

    def __init__(self):
        # ---------- 初期セットアップ ----------
        # Sudachiのトークナイザーの初期化
        self.tokenizer_obj = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.A
        self.target_pos = {"名詞", "数詞", "接頭辞", "接尾辞"}

    def _clean_markdown(self, text: str) -> str:
        """Markdown記号や不要なフォーマットを除去する"""

        def _clean_mermaid_block(match):
            content = match.group(1)
            content = re.sub(r"%%.*", "", content)
            matches = re.findall(r"[\[\(\{\<]+(.*?)[\]\)\}\>]+", content)
            return "\n".join(matches)

        clean_text = re.sub(
            r"```mermaid(.*?)```", _clean_mermaid_block, text, flags=re.DOTALL
        )
        clean_text = re.sub(r".*#.*", "", clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r"\d+\.\s+", "", clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r"[-\*\|]", "", clean_text)
        clean_text = re.sub(r"[^\S\r\n]+", "", clean_text)
        clean_text = re.sub(r"[|\│]", "", clean_text)
        clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
        return clean_text

    def _is_valid_compound(self, compound_str: str) -> bool:
        """数字以外の1文字のノイズを除外する"""
        return len(compound_str) > 1 or compound_str.isdigit()

    def _extract_compounds(self, text: str) -> List[str]:
        """形態素解析により複合語を抽出する"""
        tokens = self.tokenizer_obj.tokenize(text, self.mode)
        compounds = []
        current_compound = ""

        for token in tokens:
            pos = token.part_of_speech()
            top_pos = pos[0]

            if top_pos in self.target_pos:
                current_compound += token.surface()
            else:
                if current_compound:
                    if self._is_valid_compound(current_compound):
                        compounds.append(current_compound)
                    current_compound = ""

        if current_compound and self._is_valid_compound(current_compound):
            compounds.append(current_compound)

        return compounds

    def _filter_excluded_words(
        self, words: List[str], exact_excludes: Set[str], partial_excludes: Set[str]
    ) -> List[str]:
        """明示的に渡された除外リストに基づくフィルタリング"""
        filtered = []
        for word in words:
            if word in exact_excludes:
                continue

            if any(key in word for key in partial_excludes) and len(word) <= 20:
                continue

            filtered.append(word)
        return filtered

    def evaluate(
        self,
        llm_output: str,
        source_text: str,
        exact_excludes: Optional[Set[str]] = None,
        partial_excludes: Optional[Set[str]] = None,
        clean_markdown: bool = True,
    ) -> GroundingResult:
        """
        生成文と原文を比較し、グラウンディングスコア（P_src）を算出する
        """
        # Noneの場合は空のSetとして扱う
        exact_excludes = exact_excludes or set()
        partial_excludes = partial_excludes or set()

        # 1. テキストのクリーニング
        if clean_markdown:
            llm_output = self._clean_markdown(llm_output)

        # 2. 複合語の抽出とフィルタリング
        raw_words = self._extract_compounds(llm_output)
        target_words = self._filter_excluded_words(
            raw_words, exact_excludes, partial_excludes
        )

        # 3. 原文との照合
        found_words = [w for w in target_words if w in source_text]
        missing_words = [w for w in target_words if w not in source_text]

        # 4. スコア計算
        total_words = len(target_words)
        score = len(found_words) / total_words if total_words > 0 else 0.0

        return GroundingResult(
            score=score,
            found_words=found_words,
            missing_words=missing_words,
        )

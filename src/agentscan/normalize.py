import base64
import unicodedata

ZERO_WIDTH_TRANSLATION = str.maketrans("", "", "\u200b\u200c\u200d\ufeff")


class NormalizedText:
    def __init__(self, raw: str) -> None:
        self._raw = raw
        self._cache: dict[str, str] = {"raw": raw}

    def get(self, view: str) -> str:
        if view not in self._cache:
            self._cache[view] = self._compute(view)
        return self._cache[view]

    def _compute(self, view: str) -> str:
        if view == "nfkc":
            return unicodedata.normalize("NFKC", self._raw)
        if view == "zero_width_stripped":
            return self.get("nfkc").translate(ZERO_WIDTH_TRANSLATION)
        if view == "decoded_base64_if_applicable":
            candidate = self.get("zero_width_stripped").strip()
            try:
                decoded = base64.b64decode(candidate, validate=True)
            except (ValueError, UnicodeDecodeError):
                return candidate
            try:
                return decoded.decode("utf-8")
            except UnicodeDecodeError:
                return candidate
        raise KeyError(f"Unknown normalized view: {view}")

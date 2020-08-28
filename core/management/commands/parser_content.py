class ParserContent:
    """Classe responsável por realizar o Parser dos valores dos models"""

    def __init__(self, keys: list, contents: list, snippet: str):
        super().__init__()
        self.snippet = snippet
        self.keys = keys
        self.contents = contents

    def replace(self) -> str:
        """Método para realizar o replace das chaves do snippet pelo conteúdo.

        Returns:
            str: Conteúdo a ser salvo no arquivo definitivo da class/model.

        Raises:
            Quando os valores de keys e contents tem tamanho diferentes.
            Quando algum valor de keys contents ou snippet não for informado.
        """
        data_result = ""
        try:
            if (
                len(self.keys) == 0
                or len(self.contents) == 0
                or len(self.snippet.strip()) == 0
            ):
                raise Exception(
                    "É necessário informar os valores keys, contents e snippet, e os mesmo não podem ser brancos."
                )
            if len(self.keys) != len(self.contents):
                raise Exception("Tamanho dos atributos keys e contents deve ser igual.")
            for index, key in enumerate(self.keys):
                self.snippet = self.snippet.replace(key, self.contents[index])
            data_result = self.snippet
        except Exception as error:
            return f"\nOcorreu o erro: \n    {error}.\n"

        return data_result.strip()

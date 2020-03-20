import pytest

from tabledata import TableData
from tabledata.normalizer import TableDataNormalizer


class Test_TableDataNormalizer:
    @pytest.mark.parametrize(
        ["table_name", "headers", "rows", "expected"],
        [
            [
                "normal",
                ["a", "b_c"],
                [[1, 2], [3, 4]],
                TableData("normal", ["a", "b_c"], [[1, 2], [3, 4]]),
            ],
            [
                "underscore_char",
                ["data", "_data", "data_", "_data_"],
                [[1, 2, 3, 4], [11, 12, 13, 14]],
                TableData(
                    "underscore_char",
                    ["data", "_data", "data_", "_data_"],
                    [[1, 2, 3, 4], [11, 12, 13, 14]],
                ),
            ],
            [
                "multibyte csv",
                ["姓", "名", "生年月日", "郵便番号", "住所", "電話番号"],
                [
                    ["山田", "太郎", "2001/1/1", "100-0002", "東京都千代田区皇居外苑", "03-1234-5678"],
                    ["山田", "次郎", "2001/1/2", "251-0036", "神奈川県藤沢市江の島１丁目", "03-9999-9999"],
                ],
                TableData(
                    "multibyte csv",
                    ["姓", "名", "生年月日", "郵便番号", "住所", "電話番号"],
                    [
                        ["山田", "太郎", "2001/1/1", "100-0002", "東京都千代田区皇居外苑", "03-1234-5678"],
                        ["山田", "次郎", "2001/1/2", "251-0036", "神奈川県藤沢市江の島１丁目", "03-9999-9999"],
                    ],
                ),
            ],
        ],
    )
    def test_normal(self, table_name, headers, rows, expected):
        new_tabledata = TableDataNormalizer(TableData(table_name, headers, rows)).normalize()

        assert new_tabledata.equals(expected)

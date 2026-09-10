#!/usr/bin/env python3
from __future__ import annotations

from html import escape
from pathlib import Path
import re

from build_precinct_masterplans import PROJECTS
from integrate_precinct_masterplans import tower_display

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- TOWER_EDITORIAL_START -->"
END = "<!-- TOWER_EDITORIAL_END -->"
CSS = '<link rel="stylesheet" href="/assets/css/tower-editorial.css?v=20260910-2">'

PROJECT_GUIDES = {
    "sapphire": {
        "intro": "The Sapphire là cụm căn hộ hình thành sớm tại Vinhomes Smart City, trải từ Sapphire 1 đến Sapphire 4. Điểm đáng chú ý khi xem mặt bằng là các tòa không dùng một kiểu layout duy nhất: có tòa chữ Z, có tòa chữ U và mật độ căn trên sàn cũng thay đổi theo từng cụm.",
        "buyer": "Với nhóm Sapphire, người mua ở thực thường quan tâm nhiều đến khoảng cách tới trường học, công viên, đường nội khu và tình trạng căn đã sử dụng; nhà đầu tư lại chú ý thêm thanh khoản của từng loại căn. Vì vậy, cùng là căn 2 phòng ngủ nhưng tòa, trục và hiện trạng có thể tạo chênh lệch đáng kể về mức giá giao dịch.",
        "types": "Studio, 1PN, 1PN+1, 2PN, 2PN+1 và 3PN là các nhóm căn phổ biến trong toàn cụm Sapphire. Dải diện tích thay đổi theo từng tòa và từng giai đoạn mở bán nên khi tra một căn cụ thể cần đối chiếu đúng mã căn trên mặt bằng của tòa đang xem.",
    },
    "sakura": {
        "intro": "The Sakura gồm bốn tòa SA1, SA2, SA3 và SA5, nằm trong The Metrolines và được phát triển theo cảm hứng cảnh quan Nhật Bản. Mặt bằng của bốn tòa chia thành hai nhóm khá rõ: SA1–SA2 theo layout chữ Z, còn SA3–SA5 theo layout chữ U.",
        "buyer": "Điểm mạnh của The Sakura khi mua để ở là không gian nội khu đã có nhận diện riêng với vườn cây, đường dạo và cụm tiện ích phong cách Nhật. Khi chọn căn, nên đặt mặt bằng tòa cạnh sơ đồ phân khu để biết căn nhìn vào nội khu, về phía trường học hay ra các trục đường xung quanh.",
        "types": "Cơ cấu căn tại The Sakura trải từ Studio đến 3PN. Nhóm tòa chữ Z có mặt bằng gọn hơn, trong khi nhóm chữ U có số căn trên sàn lớn hơn và chia thành nhiều cánh; vì vậy cách đọc trục căn giữa hai nhóm không giống nhau.",
    },
    "miami": {
        "intro": "The Miami gồm GS1, GS2, GS3, GS5 và GS6. Đây là phân khu đáng chú ý vì cùng một tên thương mại nhưng có ba nhóm mặt bằng khác nhau: GS1 chữ U; GS2–GS3 chữ Z với 19 căn trên sàn điển hình; GS5–GS6 là thế hệ mặt bằng chữ Z gọn hơn với 16 vị trí căn trên sàn điển hình.",
        "buyer": "The Miami đã hình thành cảnh quan và tiện ích nội khu nên người mua có lợi thế kiểm tra trực tiếp tiếng ồn, nắng, khoảng cách giữa các tòa và tầm nhìn thực tế. Với phân khu này, chỉ nhìn số phòng ngủ là chưa đủ; cần so thêm thế hệ tòa, số căn trên sàn và vị trí trục.",
        "types": "Dải sản phẩm từ Studio đến 3PN, nhưng diện tích và cơ cấu căn thay đổi khá rõ giữa GS1, GS2–GS3 và GS5–GS6. Khi lọc tin mua bán hoặc cho thuê, nên lọc theo đúng tòa trước rồi mới so loại căn và giá.",
    },
    "tonkin": {
        "intro": "The Tonkin là cụm hai tòa TK1 và TK2, phát triển theo phong cách Indochine. Cả hai tòa đều dùng layout chữ Z, cao 38 tầng và có mật độ điển hình 16 căn/sàn, thấp hơn nhiều cụm căn hộ mở bán trước đó tại Smart City.",
        "buyer": "Với TK1 và TK2, lợi thế của mặt bằng 16 căn/sàn là việc nhận diện từng trục khá trực quan. Khi mua để ở, ngoài vị trí căn trên hành lang nên kiểm tra thêm khoảng cách tới lõi thang, tầng thực tế, ánh sáng và view; khi đầu tư cho thuê, nhóm 1PN+1 và 2PN thường là các loại căn dễ được khách so sánh trực tiếp.",
        "types": "The Tonkin có Studio, 1PN, 1PN+1, 2PN, 2PN+1 và 3PN. Mặt bằng ít căn trên sàn giúp người xem dễ đối chiếu từng mã căn hơn, nhưng vẫn cần dùng đúng sơ đồ TK1 hoặc TK2 vì mã căn giữa hai tòa không nên mặc định là tương đương.",
    },
    "masteri-west-heights": {
        "intro": "Masteri West Heights có bốn tòa West A, West B, West C và West D. Hai tòa West A–B dùng layout chữ U, cao 39 tầng, khoảng 30 căn/sàn và chia hai sảnh; West C–D dùng layout chữ Z, cao 38 tầng, khoảng 19 căn/sàn và một sảnh chính.",
        "buyer": "Đây là một trong những phân khu cần so tòa rất kỹ trước khi so giá vì cấu trúc vận hành của nhóm A–B và C–D khác nhau rõ. Một căn ở West A không nên được đem so trực tiếp với West C chỉ dựa trên diện tích; vị trí tòa, số căn/sàn, cụm thang và hướng nhìn tạo trải nghiệm khác nhau.",
        "types": "Masteri West Heights có nhiều loại căn từ Studio, 1PN+1, 2PN, 2PN+1 đến 3PN, bên cạnh một số sản phẩm đặc biệt. Các trang mặt bằng tòa tập trung vào căn hộ điển hình để người xem dễ xác định trục và bố cục trước khi đi xem nhà thực tế.",
    },
    "lumiere-evergreen": {
        "intro": "LUMIÈRE Evergreen gồm ba tòa A1 The Aqua, A2 The Atmos và A3 The Aura. A1–A2 có mặt bằng riêng với 18 căn trên sàn điển hình và hệ thang được bố trí theo từng lõi; A3 dùng cấu trúc chữ U với các nhóm tầng có cách bố trí căn khác nhau.",
        "buyer": "LUMIÈRE Evergreen thuộc nhóm căn hộ cao cấp nên khi so căn, ngoài diện tích còn cần quan tâm đến vị trí trục, mặt kính, ban công, khoảng nhìn và tiêu chuẩn bàn giao. Với A3, đặc biệt nên xem đúng nhóm tầng vì sơ đồ tầng thấp và tầng điển hình không hoàn toàn giống nhau.",
        "types": "Cơ cấu căn trải từ Studio, 1PN, 1PN+, 2PN, 2PN+ đến 3PN; một số tòa có thêm nhóm diện tích lớn. Mặt bằng từng tòa là cách nhanh nhất để biết căn nằm ở góc, giữa cánh hay gần lõi giao thông trước khi so giá bán hoặc giá thuê.",
    },
    "imperia": {
        "intro": "Imperia Smart City gồm năm tòa I1, I2, I3, I4 và I5. Đây là cụm căn hộ đã có lượng giao dịch chuyển nhượng và cho thuê tương đối ổn định, vì vậy mặt bằng từng tòa có giá trị thực tế khi người mua cần đối chiếu mã căn, tầng và vị trí trục.",
        "buyer": "Khi xem Imperia, nên tách hai việc: chọn tòa phù hợp trước, sau đó mới chọn trục căn. Các tòa nằm trong cùng một cụm nhưng vị trí tiếp cận cảnh quan, đường nội khu và khoảng cách tới tòa đối diện không hoàn toàn giống nhau; đây là những yếu tố dễ làm giá hai căn cùng diện tích khác nhau.",
        "types": "Dải căn phổ biến từ Studio đến 3PN. Vì quỹ căn chuyển nhượng khá đa dạng về nội thất và tình trạng sử dụng, mặt bằng chỉ là bước đầu; sau khi chốt trục cần xem thêm hiện trạng căn, phí dịch vụ, pháp lý và giá giao dịch thực tế.",
    },
    "canopy": {
        "intro": "The Canopy Residences gồm TC1 The Canopy Vista, TC2 The Canopy Summit và TC3 The Canopy Harmony. Ba tòa cao 38 tầng, cùng phát triển trên một cụm quy hoạch khoảng 13.136 m² và có cơ cấu căn từ Studio đến 3PN+1.",
        "buyer": "The Canopy có ba tòa đặt gần nhau nên khác biệt giữa các căn thường nằm ở vị trí trục, tầng và mặt nhìn nhiều hơn là tên phân khu. Người mua nên mở mặt bằng từng tòa song song với sơ đồ tổng thể để xác định căn quay về nội khu, tòa kế cận hay không gian phía ngoài dự án.",
        "types": "Cơ cấu sản phẩm gồm Studio, 1PN, 1PN+1, 2PN, 2PN+1, 3PN và 3PN+1. Đây là dải căn rộng, phù hợp cả người mua ở một mình, gia đình trẻ lẫn gia đình cần ba phòng ngủ; vì vậy khi so giá cần đặt đúng loại căn và đúng tòa cạnh nhau.",
    },
    "sola-park": {
        "intro": "The Sola Park gồm năm tòa G1, G2, G3, G5 và G6, cao khoảng 35 tầng. Các tòa được phát triển theo cùng một cụm dự án nhưng mỗi tòa có mặt bằng riêng, vì vậy mã căn và vị trí trục cần được đọc trên đúng sơ đồ trước khi so căn.",
        "buyer": "Sola Park có lợi thế là nguồn hàng mới hơn nhiều phân khu đã vận hành lâu năm tại Smart City. Với người mua ở thực, nên quan tâm đến thời điểm bàn giao thực tế, chất lượng hoàn thiện, vị trí tòa và khoảng nhìn; với nhà đầu tư, cần đặt giá bán cạnh tiến độ thanh toán và khả năng khai thác cho thuê sau nhận nhà.",
        "types": "Dải sản phẩm chính từ Studio đến 3PN. Các căn 1PN+1 và 2PN thường có nhiều biến thể diện tích, vì vậy việc nhìn đúng trục trên mặt bằng giúp tránh so nhầm hai căn có cùng tên loại hình nhưng khác công năng thực tế.",
    },
    "victoria": {
        "intro": "The Victoria gồm ba tòa V1 Spring, V2 Sky và V3 Shine. Mỗi tòa có 38 tầng, 2 tầng hầm, khoảng 612 căn và mặt bằng điển hình 17 căn/sàn; cơ cấu sản phẩm trải từ Studio đến 3PN+1.",
        "buyer": "Ba tòa có cấu trúc khá tương đồng nhưng vị trí trong cụm khác nhau. V1 và V3 nằm ở hai biên, trong khi V2 ở giữa; bởi vậy khi chọn căn cần xem kỹ trục, tầng và khoảng nhìn thay vì mặc định căn ở tòa biên luôn thoáng hoặc căn tòa giữa luôn bị chắn.",
        "types": "The Victoria có Studio, 1PN, 1PN+1, 2PN, 2PN+1, 3PN và 3PN+1. Nhóm căn lớn tại V1 có một số layout rộng hơn, còn ở V2–V3 việc lựa chọn thường phụ thuộc nhiều vào trục và mặt nhìn cụ thể.",
    },
}

SOLAPARK_NAMES = {"g1": "G1 The Garden", "g2": "G2 The Aqua", "g3": "G3 The Metro", "g5": "G5 The Avenue", "g6": "G6 The Sky"}
VICTORIA_NAMES = {"v1": "V1 Spring", "v2": "V2 Sky", "v3": "V3 Shine"}


def detail_for(project: dict, tower: str) -> dict:
    slug = project["slug"]
    display = tower_display(project, tower)
    if slug == "sapphire":
        group = tower.split("-", 1)[0]
        if group == "s1":
            if tower == "s1-03":
                return {"fact": "S1.03 là tòa layout chữ U trong Sapphire 1, khác nhóm S1.01, S1.02, S1.05 và S1.06 dùng layout chữ Z. Mặt bằng chữ U có mật độ khoảng 30 căn/sàn và chia nhiều cánh hơn.", "angle": "Nếu đang cân S1.03 với các tòa chữ Z cùng cụm, hãy chú ý số căn trên sàn, vị trí lõi thang và khoảng cách từ căn đến sảnh thang thay vì chỉ nhìn diện tích."}
            return {"fact": f"{display} thuộc Sapphire 1 và dùng layout chữ Z. Nhóm tòa chữ Z tại Sapphire 1 có khoảng 19 căn/sàn, 6 thang máy và 2 thang thoát hiểm; chiều cao các tòa trong cụm khoảng 34–35 tầng.", "angle": f"Khi so {display} với S1.03, khác biệt lớn nhất nằm ở hình khối Z và U. Với người mua ở thực, layout chữ Z gọn hơn giúp việc nhận diện trục góc và vị trí căn trên hành lang khá trực quan."}
        if group == "s2":
            layout = "chữ U" if tower in {"s2-01", "s2-02"} else "chữ Z"
            peers = "S2.01–S2.02" if layout == "chữ U" else "S2.03–S2.05"
            return {"fact": f"{display} thuộc Sapphire 2, dùng layout {layout}. Trong cụm này, S2.01–S2.02 là nhóm chữ U còn S2.03–S2.05 là nhóm chữ Z; chiều cao các tòa dao động khoảng 30–35 tầng.", "angle": f"Nếu ưu tiên so các căn có trải nghiệm mặt bằng gần nhau, nên đặt {display} cạnh nhóm {peers} trước. Sau đó mới mở sang nhóm layout còn lại để thấy rõ khác biệt về hành lang và vị trí trục."}
        if group == "s3":
            return {"fact": f"{display} thuộc Sapphire 3. Cả ba tòa S3.01, S3.02 và S3.03 đều dùng layout chữ Z, cao 38 tầng và có mật độ điển hình khoảng 19 căn/sàn.", "angle": f"Vì ba tòa Sapphire 3 có cấu trúc mặt bằng khá gần nhau, khi so {display} với hai tòa còn lại nên tập trung vào vị trí trong cụm, tầng, hướng nhìn và khoảng chắn thực tế."}
        return {"fact": f"{display} thuộc Sapphire 4, cụm ba tòa S4.01, S4.02 và S4.03 cao khoảng 35 tầng. Tài liệu thị trường về tên gọi hình khối có một số khác biệt, vì vậy nên ưu tiên đọc trực tiếp sơ đồ HD của đúng tòa.", "angle": f"Với {display}, phần đáng xem nhất là vị trí từng trục trên mặt bằng và tương quan với hai tòa còn lại của Sapphire 4. Không nên lấy mã căn của một tòa để suy sang tòa khác."}
    if slug == "sakura":
        data = {
            "sa1": ("layout chữ Z, khoảng 19 căn/sàn và cao 37 tầng", "SA1 nằm trong nhóm mặt bằng gọn cùng SA2; khi chọn căn nên chú ý trục nhìn về nội khu Sakura, phía The Miami và khu trường học."),
            "sa2": ("layout chữ Z, cao 38 tầng, khoảng 19 căn/sàn, 6 thang máy và 2 thang thoát hiểm", "SA2 là một trong những tòa có thông tin mặt bằng khá đầy đủ; đây là lựa chọn phù hợp để so trực tiếp các trục Studio đến 3PN trên cùng một sơ đồ."),
            "sa3": ("layout chữ U, cao 39 tầng và khoảng 30 căn/sàn", "SA3 có số căn trên sàn lớn hơn nhóm SA1–SA2, vì vậy nên xem kỹ căn thuộc cánh nào của chữ U và khoảng cách tới cụm thang gần nhất."),
            "sa5": ("layout chữ U, cao 39 tầng và khoảng 30 căn/sàn", "SA5 cùng nhóm chữ U với SA3 và được nhận diện thêm bởi không gian tiện ích trên cao. Khi chọn căn nên so các trục hướng nội khu với phía trường học và đường nội khu trên sơ đồ tổng."),
        }
        fact, angle = data[tower]
        return {"fact": f"{display} có {fact}. Cơ cấu căn trải từ Studio đến 3PN và được bố trí theo nhiều trục quanh lõi giao thông trung tâm.", "angle": angle}
    if slug == "miami":
        if tower == "gs1":
            return {"fact": "GS1 là tòa chữ U của The Miami, với khoảng 30 căn trên mặt bằng tầng điển hình. Đây là cấu trúc khác rõ so với bốn tòa chữ Z còn lại.", "angle": "GS1 phù hợp để xem theo từng cánh của chữ U. Khi so với GS2–GS3 hoặc GS5–GS6, cần đặt lại kỳ vọng về số căn trên sàn, độ dài hành lang và vị trí các căn góc."}
        if tower in {"gs2", "gs3"}:
            return {"fact": f"{display} thuộc nhóm chữ Z thế hệ GS2–GS3, với khoảng 19 căn/sàn. Riêng GS2 có hồ sơ công bố 703 căn và hệ 6 thang máy.", "angle": f"{display} nên được so trước với {'GS3' if tower == 'gs2' else 'GS2'} vì hai tòa có cấu trúc gần nhau hơn. Sau đó mới so sang GS5–GS6, nơi mật độ trên sàn thấp hơn."}
        return {"fact": f"{display} thuộc nhóm GS5–GS6, mặt bằng hiện hành thể hiện 16 vị trí căn trên sàn điển hình. Đây là nhóm có mật độ gọn hơn GS1 và GS2–GS3.", "angle": f"Với {display}, điểm đáng chú ý là tỷ lệ căn trên lõi giao thông thấp hơn các thế hệ tòa trước. Khi so giá, nên chọn căn cùng loại và cùng nhóm GS5–GS6 để kết quả sát thực tế hơn."}
    if slug == "tonkin":
        other = "TK2" if tower == "tk1" else "TK1"
        return {"fact": f"{display} cao 38 tầng, layout chữ Z và khoảng 16 căn/sàn. Cấu trúc mật độ thấp là điểm khác biệt dễ thấy của The Tonkin so với nhiều tòa Sapphire và các tòa chữ U.", "angle": f"Khi so {display} với {other}, nên đối chiếu từng mã căn trên hai mặt bằng riêng. Hai tòa có cùng ngôn ngữ thiết kế nhưng không nên mặc định vị trí CH01, CH02… là giống nhau."}
    if slug == "masteri-west-heights":
        if tower in {"west-a", "west-b"}:
            other = "West B" if tower == "west-a" else "West A"
            return {"fact": f"{display} thuộc nhóm West A–B: layout chữ U, cao 39 tầng, khoảng 30 căn/sàn và hệ 12 thang máy chia thành 2 sảnh.", "angle": f"Nếu đang cân giữa {display} và {other}, hãy so vị trí trục và mặt nhìn. Nếu so sang West C–D, cần nhớ hai nhóm khác cả hình khối lẫn số căn trên sàn nên không thể chỉ lấy đơn giá/m² làm tiêu chí duy nhất."}
        other = "West D" if tower == "west-c" else "West C"
        return {"fact": f"{display} thuộc nhóm West C–D: layout chữ Z, cao 38 tầng, khoảng 19 căn/sàn và một sảnh chính với 6 thang máy.", "angle": f"{display} có mặt bằng gọn hơn West A–B. Nên so trước với {other}, sau đó mới đối chiếu sang nhóm chữ U để thấy rõ khác biệt về mật độ, lõi thang và cách bố trí căn."}
    if slug == "lumiere-evergreen":
        data = {
            "a1": ("A1 The Aqua có mặt bằng 39 tầng, 18 căn/sàn điển hình và 9 thang máy", "A1 nên được đọc theo vị trí từng trục quanh lõi thang; nhóm căn góc và nhóm căn giữa có khác biệt rõ về số mặt thoáng."),
            "a2": ("A2 The Atmos có mặt bằng 39 tầng, 18 căn/sàn điển hình và 9 thang máy", "A2 có cấu trúc gần A1 nhưng không nên dùng mã căn A1 để suy sang A2. Khi so hai tòa, hãy đặt đúng sơ đồ cạnh nhau và so từng trục tương ứng."),
            "a3": ("A3 The Aura cao 39 tầng và dùng cấu trúc chữ U; các nhóm tầng 2–5, 6–11, 12–19 và 21–39 có cách bố trí cần xem riêng", "A3 là tòa cần đọc mặt bằng theo nhóm tầng thay vì chỉ xem một sơ đồ đại diện. Khi tìm căn cụ thể, tầng của căn là thông tin bắt buộc trước khi kết luận vị trí trục."),
        }
        fact, angle = data[tower]
        return {"fact": fact + ". Dải căn từ Studio đến 3PN/3PN+ tùy tòa và nhóm tầng.", "angle": angle}
    if slug == "canopy":
        name = {"tc1": "The Canopy Vista", "tc2": "The Canopy Summit", "tc3": "The Canopy Harmony"}[tower]
        return {"fact": f"{display} ({name}) là một trong ba tòa của The Canopy Residences, cao 38 tầng. Cơ cấu sản phẩm trải từ Studio đến 3PN+1, phù hợp nhiều nhu cầu ở thực và đầu tư cho thuê.", "angle": f"Khi xem {display}, nên đặt mặt bằng cạnh TC1–TC3 tổng thể để biết vị trí tòa trong cụm. Sau đó mới đọc mã căn, tầng và mặt nhìn; đây là cách tránh nhầm khi ba tòa có tên thương mại khá giống nhau."}
    if slug == "sola-park":
        full = SOLAPARK_NAMES[tower]
        return {"fact": f"{full} thuộc cụm năm tòa The Sola Park, cao khoảng 35 tầng. Tòa có sơ đồ tầng riêng và cơ cấu căn từ Studio đến 3PN.", "angle": f"Với {full}, nên xem mặt bằng cùng tiến độ và hiện trạng bàn giao của chính tòa. Khi so với các tòa G khác, ưu tiên căn cùng loại, cùng nhóm tầng và tương đồng về thời điểm nhận nhà."}
    if slug == "victoria":
        full = VICTORIA_NAMES[tower]
        position = {"v1": "tòa biên một phía của cụm", "v2": "tòa nằm giữa V1 và V3", "v3": "tòa biên phía còn lại của cụm"}[tower]
        return {"fact": f"{full} có 38 tầng, 2 tầng hầm, khoảng 612 căn và 17 căn trên mặt bằng tầng điển hình. Đây là {position}.", "angle": f"Khi chọn căn tại {full}, vị trí trục và khoảng nhìn quan trọng hơn nhận xét chung về tòa. Căn góc, căn giữa và căn hướng vào khoảng nội khu có thể cho trải nghiệm rất khác dù cùng số phòng ngủ."}
    return {"fact": f"{display} là một trong các tòa thuộc {project['name']}, có mặt bằng riêng để đối chiếu mã căn và vị trí từng trục.", "angle": f"Khi chọn căn tại {display}, nên so những căn cùng loại, cùng nhóm tầng và tương đồng về nội thất trước khi đánh giá mức giá hợp lý."}


def sibling_links(project: dict, tower: str) -> str:
    slug = project["slug"]
    idx = project["towers"].index(tower)
    candidates = []
    for offset in (-1, 1):
        j = idx + offset
        if 0 <= j < len(project["towers"]):
            sibling = project["towers"][j]
            candidates.append((sibling, tower_display(project, sibling)))
    if not candidates:
        candidates = [(s, tower_display(project, s)) for s in project["towers"] if s != tower][:2]
    items = []
    for sibling, name in candidates:
        items.append(f'<a href="/mat-bang-smart-city/{slug}/{sibling}/"><strong>Mặt bằng {escape(name)}</strong><span>So trực tiếp layout và vị trí trục với tòa đang xem.</span></a>')
    items.append(f'<a href="/mat-bang-smart-city/{slug}/"><strong>Mặt bằng tổng {escape(project["name"])}</strong><span>Xem vị trí các tòa trong toàn phân khu trước khi chốt căn.</span></a>')
    return "".join(items)


def facts_markup(project: dict) -> str:
    return "".join(f"<span>{escape(fact)}</span>" for fact in project.get("facts", []))


def editorial_block(project: dict, tower: str) -> str:
    slug = project["slug"]
    name = project["name"]
    display = tower_display(project, tower)
    guide = PROJECT_GUIDES[slug]
    detail = detail_for(project, tower)
    comparisons = sibling_links(project, tower)
    facts = facts_markup(project)
    return f'''{START}
<section class="section tower-editorial" id="tim-hieu-toa-{escape(tower)}" aria-labelledby="tower-editorial-title">
  <div class="container tower-editorial__container">
    <header class="tower-editorial__hero">
      <div>
        <p class="eyebrow section-kicker">Mặt bằng · loại căn · kinh nghiệm chọn căn</p>
        <h2 id="tower-editorial-title">Mặt bằng {escape(display)} {escape(name)}: thông tin cần biết trước khi mua hoặc thuê</h2>
      </div>
      <p class="tower-editorial__lead">{escape(detail['fact'])}</p>
    </header>

    <div class="tower-editorial__facts" aria-label="Thông tin nhanh">{facts}</div>

    <div class="tower-editorial__intro">
      <article>
        <h3>Tổng quan tòa {escape(display)}</h3>
        <p>{escape(guide['intro'])}</p>
        <p>Riêng <strong>{escape(display)}</strong>, {escape(detail['fact'][0].lower() + detail['fact'][1:])} Đây là thông tin nên xem trước khi đi sâu vào từng mã căn, bởi cùng một loại căn nhưng đặt ở hai layout khác nhau có thể cho cách bố trí hành lang, khoảng cách tới thang máy và số mặt thoáng khác nhau.</p>
      </article>
      <article>
        <h3>Điểm đáng chú ý trên mặt bằng {escape(display)}</h3>
        <p>{escape(detail['angle'])}</p>
        <p>Khi mở ảnh mặt bằng HD, nên bắt đầu từ lõi thang ở giữa tòa, sau đó lần theo từng cánh để tìm đúng mã căn. Căn góc thường có thêm mặt thoáng; căn giữa hành lang thường có hình khối vuông vắn hơn; các căn gần lõi thang thuận tiện di chuyển nhưng cần kiểm tra tiếng ồn thực tế. Đây là các tiêu chí có thể dùng ngay khi đi xem nhà.</p>
      </article>
    </div>

    <div class="tower-editorial__section-head">
      <div><p class="eyebrow section-kicker">Thiết kế căn hộ</p><h2>Các loại căn tại {escape(display)} và cách đọc layout</h2></div>
      <p>{escape(guide['types'])}</p>
    </div>
    <div class="tower-editorial__cards">
      <article class="tower-editorial-card">
        <h3>Studio và 1 phòng ngủ</h3>
        <p>Nhóm căn nhỏ thường được quan tâm bởi người mua độc thân, cặp đôi trẻ hoặc nhà đầu tư cho thuê. Khi xem mặt bằng {escape(display)}, nên để ý bề ngang mặt thoáng, vị trí cửa vào, khu bếp và khoảng cách từ phòng ngủ tới logia. Hai căn cùng diện tích nhưng khác trục có thể khác đáng kể về ánh sáng và cách kê nội thất.</p>
      </article>
      <article class="tower-editorial-card">
        <h3>1PN+1 và 2 phòng ngủ</h3>
        <p>Đây là nhóm căn có nhu cầu ở thực lớn tại Smart City. Không gian “+1” có thể dùng làm góc làm việc, phòng ngủ nhỏ hoặc kho tùy layout. Với căn 2PN, cần nhìn thêm số nhà vệ sinh, vị trí phòng khách so với logia và độ riêng tư của hai phòng ngủ. Mặt bằng tòa giúp loại nhanh những trục không hợp nhu cầu trước khi đi xem thực tế.</p>
      </article>
      <article class="tower-editorial-card">
        <h3>2PN+1 và 3 phòng ngủ</h3>
        <p>Nhóm căn lớn phù hợp gia đình nhiều thành viên và thường có tổng giá cao hơn rõ rệt. Khi lựa chọn, ngoài diện tích nên ưu tiên cách bố trí phòng ngủ, số mặt thoáng, vị trí căn góc và chiều dài hành lang từ thang máy tới cửa căn. Nếu mua để ở lâu dài, công năng thực tế quan trọng hơn chênh lệch vài mét vuông trên giấy.</p>
      </article>
    </div>

    <div class="tower-editorial__checklist">
      <div class="tower-editorial__checklist-copy">
        <p class="eyebrow section-kicker">Kinh nghiệm xem căn</p>
        <h2>Chọn căn {escape(display)} nên kiểm tra những gì?</h2>
        <p>{escape(guide['buyer'])}</p>
      </div>
      <ol>
        <li><strong>Xác định đúng mã căn.</strong><span>Mở sơ đồ HD, tìm đúng trục rồi kiểm tra căn nằm ở góc, giữa hành lang hay gần lõi thang.</span></li>
        <li><strong>Kiểm tra tầng và khoảng nhìn.</strong><span>Cùng một trục nhưng tầng thấp, tầng trung và tầng cao có thể khác về tiếng ồn, nắng và vật cản phía trước.</span></li>
        <li><strong>Xem hiện trạng căn.</strong><span>Đối chiếu nội thất, tường sàn, thiết bị, điều hòa, logia và các hạng mục đã sửa so với bàn giao ban đầu.</span></li>
        <li><strong>So giá đúng nhóm.</strong><span>Nên so với căn cùng tòa, cùng loại, diện tích gần nhau và tình trạng nội thất tương đương trước khi mở rộng sang tòa khác.</span></li>
      </ol>
    </div>

    <div class="tower-editorial__section-head">
      <div><p class="eyebrow section-kicker">So sánh cùng phân khu</p><h2>Nên so {escape(display)} với tòa nào?</h2></div>
      <p>So tòa liền kề là cách nhanh nhất để biết khác biệt đến từ mặt bằng hay chỉ đến từ nội thất và giá chào bán. Các liên kết dưới đây mở thẳng sang những tòa gần nhất trong cùng phân khu.</p>
    </div>
    <div class="tower-editorial__compare">{comparisons}</div>

    <div class="tower-editorial__faq" id="faq-mat-bang-{escape(tower)}">
      <div class="tower-editorial__section-head">
        <div><p class="eyebrow section-kicker">Câu hỏi thường gặp</p><h2>FAQ về mặt bằng {escape(display)}</h2></div>
        <p>Những câu hỏi dưới đây thường xuất hiện khi khách bắt đầu từ bản vẽ mặt bằng rồi chuyển sang tìm căn đang bán hoặc cho thuê.</p>
      </div>
      <details open><summary>Mặt bằng {escape(display)} xem được những thông tin gì?</summary><p>Mặt bằng cho biết vị trí lõi thang, hành lang, từng trục căn và quan hệ giữa các căn trên cùng một tầng. Đây là cơ sở để xác định căn góc, căn giữa, vị trí gần thang và cách bố trí từng cánh của tòa trước khi đi xem nhà.</p></details>
      <details><summary>Làm sao biết căn {escape(display)} có hướng và view nào?</summary><p>Cần đặt mặt bằng tòa cạnh sơ đồ tổng thể của {escape(name)} và kiểm tra thêm tầng thực tế. Hướng ban công có thể đọc khi sơ đồ thể hiện định hướng rõ; còn view cần tính cả khoảng cách, công trình phía trước và hiện trạng thực tế tại thời điểm xem căn.</p></details>
      <details><summary>Nên chọn tầng thấp, tầng trung hay tầng cao ở {escape(display)}?</summary><p>Không có một tầng tốt cho tất cả nhu cầu. Tầng thấp thuận tiện di chuyển và dễ quan sát cảnh quan gần; tầng trung thường cân bằng giữa độ cao và thời gian đi thang; tầng cao có tầm nhìn rộng hơn nhưng cần kiểm tra gió, nắng và thời gian chờ thang vào giờ cao điểm.</p></details>
      <details><summary>Sau khi xem mặt bằng {escape(display)}, tìm căn đang giao dịch ở đâu?</summary><p>Có thể xem <a href="/mua-ban-smart-city/">căn hộ Smart City đang bán</a> hoặc <a href="/cho-thue-smart-city/">căn hộ Smart City đang cho thuê</a>. Khi lọc tin, hãy ưu tiên đúng tòa {escape(display)}, sau đó chọn loại căn, khoảng giá và tình trạng nội thất phù hợp.</p></details>
    </div>

    <div class="tower-editorial__cta">
      <div><p class="eyebrow section-kicker">Tìm căn thực tế</p><h2>Xem căn {escape(display)} đang bán và cho thuê</h2><p>Sau khi xác định được tòa, loại căn và trục phù hợp, bước tiếp theo là so quỹ căn thực tế theo giá, tầng và nội thất.</p></div>
      <div class="tower-editorial__cta-actions"><a class="btn btn-primary" href="/mua-ban-smart-city/">Xem căn đang bán</a><a class="btn" href="/cho-thue-smart-city/">Xem căn cho thuê</a></div>
    </div>
  </div>
</section>
{END}'''


def ensure_css(text: str) -> str:
    pattern = r'<link[^>]+href=["\']/assets/css/tower-editorial\.css\?v=[^"\']+["\'][^>]*>'
    if "tower-editorial.css" in text:
        return re.sub(pattern, CSS, text, count=1)
    theme = re.search(r'<link[^>]+href=["\']/assets/css/site-theme\.css[^>]*>', text)
    if theme:
        return text[:theme.start()] + CSS + text[theme.start():]
    return text.replace("</head>", CSS + "</head>", 1)


def humanize_technical_intro(text: str, project: dict, tower: str) -> str:
    display = tower_display(project, tower)
    name = project["name"]
    replacements = {
        f"Trang này là hồ sơ riêng của {display}. Dùng đúng mặt bằng của tòa trước khi kết luận mã căn, vị trí lõi thang, trục góc, hướng/view hoặc so giá với căn khác.": f"Mặt bằng {display} giúp xác định vị trí từng trục căn, lõi thang và hành lang trước khi so giá hoặc đi xem nhà thực tế.",
        f"Thuộc <strong>{display}</strong>. URL riêng của hồ sơ này giúp người dùng và công cụ tìm kiếm không phải suy tòa từ một trang mặt bằng tổng.": f"Thuộc <strong>{name}</strong>. Mở ảnh HD để xem rõ mã căn, vị trí căn góc và khoảng cách tới lõi thang.",
        f"Chuyển ngang giữa các tòa để so đúng mặt bằng thay vì quay lại Google hoặc dùng nhầm sơ đồ của tòa khác.": "Có thể mở nhanh các tòa cùng phân khu để so layout, mật độ căn và vị trí trục trước khi chọn căn.",
        "<p class=\"tower-data-note\"><strong>Nguyên tắc dữ liệu:</strong> chỉ dùng thông số có trong hồ sơ hiện có; không tự suy hướng, view, mật độ hoặc diện tích khi chưa đủ căn cứ.</p>": "<p class=\"tower-data-note\"><strong>Lưu ý khi xem căn:</strong> hướng và tầm nhìn nên được kiểm tra trên sơ đồ tổng thể và đối chiếu thực tế tại đúng tầng đang quan tâm.</p>",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("Mặt bằng tòa · hồ sơ HD · liên kết phân khu", "Mặt bằng tòa · ảnh HD · căn hộ điển hình")
    text = text.replace("Mặt bằng tòa ", "Mặt bằng tòa ", 1)
    text = text.replace("<p class=\"eyebrow section-kicker\">Cách đọc đúng</p>", "<p class=\"eyebrow section-kicker\">Xem nhanh mặt bằng</p>")
    text = text.replace("<strong>Đúng tòa:</strong>", "<strong>Mã tòa:</strong>")
    text = text.replace("<strong>Đúng bản vẽ:</strong>", "<strong>Ảnh HD:</strong>")
    text = text.replace("<strong>Đúng dữ kiện:</strong>", "<strong>Hướng & view:</strong>")
    return text


def inject(project: dict, tower: str) -> None:
    path = ROOT / "mat-bang-smart-city" / project["slug"] / tower / "index.html"
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), "", text, flags=re.S)
    text = humanize_technical_intro(text, project, tower)
    text = ensure_css(text)
    block = editorial_block(project, tower)
    marker = "<!-- TOWER_FLOORPLAN_INTENT_END -->"
    if marker in text:
        text = text.replace(marker, marker + block, 1)
    else:
        text = text.replace("</main>", block + "</main>", 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    count = 0
    for project in PROJECTS:
        for tower in project["towers"]:
            inject(project, tower)
            count += 1
    print(f"natural real-estate editorial content generated: {count} tower pages")


if __name__ == "__main__":
    main()

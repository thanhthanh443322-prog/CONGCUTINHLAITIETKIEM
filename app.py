import streamlit as st
st.image("")
import pandas as pd

# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Tính lãi gửi tiết kiệm",
    page_icon="💰",
    layout="centered"
)

st.title("💰 TÍNH LÃI GỬI TIẾT KIỆM")
st.caption("Công cụ tính lãi tiền gửi theo lãi đơn hoặc lãi kép")

# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def format_money(value):
    return f"{value:,.0f} VNĐ"


# =========================
# NHẬP THÔNG TIN
# =========================
st.subheader("📌 Thông tin khoản tiền gửi")

tien_gui = st.number_input(
    "Số tiền gửi (VNĐ)",
    min_value=0.0,
    value=100_000_000.0,
    step=1_000_000.0,
    format="%.0f"
)

ky_han = st.number_input(
    "Kỳ hạn (tháng)",
    min_value=1,
    max_value=120,
    value=12,
    step=1
)

lai_suat = st.number_input(
    "Lãi suất (%/năm)",
    min_value=0.0,
    max_value=100.0,
    value=6.0,
    step=0.1,
    format="%.2f"
)

hinh_thuc_nhan_lai = st.selectbox(
    "Hình thức nhận lãi",
    [
        "Cuối kỳ",
        "Hàng tháng",
        "Hàng quý"
    ]
)

loai_lai = st.radio(
    "Phương pháp tính lãi",
    [
        "Lãi đơn",
        "Lãi kép"
    ],
    horizontal=True
)

st.divider()


# =========================
# TÍNH TOÁN
# =========================
if st.button("🧮 TÍNH LÃI", type="primary", use_container_width=True):

    if tien_gui <= 0:
        st.error("Vui lòng nhập số tiền gửi lớn hơn 0.")
        st.stop()

    if lai_suat < 0:
        st.error("Lãi suất không được nhỏ hơn 0.")
        st.stop()

    # Lãi suất theo tháng
    lai_suat_thang = lai_suat / 100 / 12

    # Xác định số kỳ nhận lãi
    if hinh_thuc_nhan_lai == "Hàng tháng":
        so_ky = ky_han
        so_thang_moi_ky = 1

    elif hinh_thuc_nhan_lai == "Hàng quý":
        so_ky = ky_han // 3
        so_thang_moi_ky = 3

        # Nếu kỳ hạn không chia hết cho 3,
        # phần tháng lẻ sẽ được tính ở cuối kỳ.
        thang_le = ky_han % 3

    else:
        so_ky = 1
        so_thang_moi_ky = ky_han

    # =========================
    # LÃI ĐƠN
    # =========================
    if loai_lai == "Lãi đơn":

        tong_lai = tien_gui * (lai_suat / 100) * (ky_han / 12)
        tong_tien = tien_gui + tong_lai

        if hinh_thuc_nhan_lai == "Cuối kỳ":

            bang_du_lieu = pd.DataFrame({
                "Kỳ": [f"{ky_han} tháng"],
                "Tiền gốc": [tien_gui],
                "Tiền lãi": [tong_lai],
                "Tổng tiền nhận": [tong_tien]
            })

        else:

            lai_moi_ky = tien_gui * (lai_suat / 100) * (
                so_thang_moi_ky / 12
            )

            du_lieu = []

            for i in range(1, so_ky + 1):
                tien_lai_ky = lai_moi_ky

                du_lieu.append({
                    "Kỳ": i,
                    "Thời gian": f"{i * so_thang_moi_ky} tháng",
                    "Tiền gốc": tien_gui,
                    "Tiền lãi kỳ này": tien_lai_ky,
                    "Lãi lũy kế": lai_moi_ky * i
                })

            # Tính phần tháng lẻ đối với nhận lãi hàng quý
            if (
                hinh_thuc_nhan_lai == "Hàng quý"
                and thang_le > 0
            ):
                lai_thang_le = tien_gui * (lai_suat / 100) * (
                    thang_le / 12
                )

                du_lieu.append({
                    "Kỳ": so_ky + 1,
                    "Thời gian": f"{ky_han} tháng",
                    "Tiền gốc": tien_gui,
                    "Tiền lãi kỳ này": lai_thang_le,
                    "Lãi lũy kế": tong_lai
                })

            bang_du_lieu = pd.DataFrame(du_lieu)

    # =========================
    # LÃI KÉP
    # =========================
    else:

        # Trường hợp nhận lãi cuối kỳ:
        # lãi nhập gốc vào cuối mỗi tháng để tính lãi kép.
        if hinh_thuc_nhan_lai == "Cuối kỳ":

            gia_tri = tien_gui * (
                1 + lai_suat_thang
            ) ** ky_han

            tong_lai = gia_tri - tien_gui
            tong_tien = gia_tri

            bang_du_lieu = pd.DataFrame({
                "Kỳ": [f"{ky_han} tháng"],
                "Tiền gốc": [tien_gui],
                "Tiền lãi": [tong_lai],
                "Tổng tiền nhận": [tong_tien]
            })

        else:

            # Với lãi kép, tiền lãi được nhập vào gốc
            # theo chu kỳ nhận lãi.
            if hinh_thuc_nhan_lai == "Hàng tháng":
                so_ky = ky_han
                so_thang_moi_ky = 1

            else:
                so_ky = ky_han // 3
                so_thang_moi_ky = 3

            du_lieu = []

            von_hien_tai = tien_gui
            tong_lai_da_nhan = 0

            for i in range(1, so_ky + 1):

                lai_ky = von_hien_tai * (
                    (1 + lai_suat_thang) ** so_thang_moi_ky - 1
                )

                von_hien_tai += lai_ky
                tong_lai_da_nhan += lai_ky

                du_lieu.append({
                    "Kỳ": i,
                    "Thời gian": f"{i * so_thang_moi_ky} tháng",
                    "Tiền gốc + lãi đầu kỳ": von_hien_tai - lai_ky,
                    "Tiền lãi kỳ này": lai_ky,
                    "Tổng tiền": von_hien_tai
                })

            # Xử lý số tháng lẻ nếu kỳ hạn không chia hết cho 3
            if (
                hinh_thuc_nhan_lai == "Hàng quý"
                and ky_han % 3 != 0
            ):
                thang_le = ky_han % 3

                lai_ky_le = von_hien_tai * (
                    (1 + lai_suat_thang) ** thang_le - 1
                )

                von_hien_tai += lai_ky_le
                tong_lai_da_nhan += lai_ky_le

                du_lieu.append({
                    "Kỳ": so_ky + 1,
                    "Thời gian": f"{ky_han} tháng",
                    "Tiền gốc + lãi đầu kỳ":
                        von_hien_tai - lai_ky_le,
                    "Tiền lãi kỳ này": lai_ky_le,
                    "Tổng tiền": von_hien_tai
                })

            tong_lai = tong_lai_da_nhan
            tong_tien = von_hien_tai

            bang_du_lieu = pd.DataFrame(du_lieu)

    # =========================
    # KẾT QUẢ
    # =========================
    st.success("Đã tính toán thành công!")

    st.subheader("📊 Kết quả")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Tiền lãi định kỳ",
            format_money(
                tong_lai / max(so_ky, 1)
            )
        )

    with col2:
        st.metric(
            "Tổng tiền lãi",
            format_money(tong_lai)
        )

    with col3:
        st.metric(
            "Tổng gốc + lãi",
            format_money(tong_tien)
        )

    st.divider()

    st.subheader("📋 Chi tiết theo kỳ")

    # Định dạng số tiền để hiển thị
    bang_hien_thi = bang_du_lieu.copy()

    for cot in bang_hien_thi.columns:
        if (
            "Tiền" in cot
            or "Lãi" in cot
            or "Tổng" in cot
            or "gốc" in cot
        ):
            bang_hien_thi[cot] = bang_hien_thi[cot].apply(
                format_money
            )

    st.dataframe(
        bang_hien_thi,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # TÓM TẮT
    # =========================
    st.subheader("📝 Tóm tắt")

    st.write(f"**Số tiền gửi:** {format_money(tien_gui)}")
    st.write(f"**Kỳ hạn:** {ky_han} tháng")
    st.write(f"**Lãi suất:** {lai_suat:.2f}%/năm")
    st.write(f"**Hình thức nhận lãi:** {hinh_thuc_nhan_lai}")
    st.write(f"**Phương pháp:** {loai_lai}")
    st.write(f"**Tổng tiền lãi:** {format_money(tong_lai)}")
    st.write(f"**Tổng số tiền nhận:** {format_money(tong_tien)}")

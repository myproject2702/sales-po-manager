import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Quản Lý Đơn Hàng Sales - Arirang", layout="wide")

st.title("📦 Phần mềm Quản Lý PO & Bảng Giá Mực In - Arirang")
st.markdown("---")

# 1. Khởi tạo Bảng giá chuẩn theo từng Khách hàng & Ngày báo giá
if "df_price_list" not in st.session_state:
    st.session_state.df_price_list = pd.DataFrame([
        {"Tên Công Ty / Khách Hàng": "Lộ Đức", "Mã SP / Quy cách": "OPP 39", "ĐVT": "Kg", "Đơn giá chuẩn (VNĐ)": 75000.0, "Ngày Báo Giá": "15/01/2026"},
        {"Tên Công Ty / Khách Hàng": "Lộ Đức", "Mã SP / Quy cách": "PE GOLD", "ĐVT": "Thùng", "Đơn giá chuẩn (VNĐ)": 139000.0, "Ngày Báo Giá": "01/02/2026"},
        {"Tên Công Ty / Khách Hàng": "Vina Úc ĐN", "Mã SP / Quy cách": "OPP 39", "ĐVT": "Kg", "Đơn giá chuẩn (VNĐ)": 78000.0, "Ngày Báo Giá": "10/03/2026"},
        {"Tên Công Ty / Khách Hàng": "Lộ Đức", "Mã SP / Quy cách": "OPP 94", "ĐVT": "Phuy", "Đơn giá chuẩn (VNĐ)": 74000.0, "Ngày Báo Giá": "20/01/2026"},
        {"Tên Công Ty / Khách Hàng": "Lộ Đức", "Mã SP / Quy cách": "PE 8365 GOLD", "ĐVT": "Kg", "Đơn giá chuẩn (VNĐ)": 85000.0, "Ngày Báo Giá": "15/02/2026"},
        {"Tên Công Ty / Khách Hàng": "Lộ Đức", "Mã SP / Quy cách": "OPP 62", "ĐVT": "Kg", "Đơn giá chuẩn (VNĐ)": 62000.0, "Ngày Báo Giá": "20/02/2026"}
    ])

# 2. Session state lưu kết quả PO
if "po_data" not in st.session_state:
    st.session_state.po_data = None

# Bảng sản phẩm mặc định trong PO
if "df_po_items" not in st.session_state:
    st.session_state.df_po_items = pd.DataFrame([
        {"Mã SP / Quy cách": "OPP 39", "Số lượng": 340.0, "ĐVT": "Kg", "Đơn giá (VNĐ)": 75000.0}
    ])

tab1, tab2 = st.tabs(["🚀 Tạo Đơn Hàng (PO)", "⚙️ Quản Lý & Cập Nhật Bảng Giá Theo Khách Hàng"])

with tab1:
    st.subheader("1. Thông tin chung đơn hàng")
    col1, col2 = st.columns(2)

    with col1:
        customer_name = st.text_input("Tên Khách Hàng / Công Ty", value="Lộ Đức", help="Tên công ty sẽ dùng để đối soát đơn giá chuẩn tương ứng!")
        po_number = st.text_input("Mã số PO", value="PO-01")
        order_date_val = st.date_input("Ngày nhận PO", value=datetime.today())
        order_date_str = order_date_val.strftime("%d/%m/%Y")
        
    with col2:
        delivery_date_val = st.date_input("Ngày yêu cầu giao hàng", value=datetime.today())
        delivery_date_str = delivery_date_val.strftime("%d/%m/%Y")
        sales_person = st.text_input("Sales phụ trách", value="Lê Thanh Duy")

    st.markdown("---")
    st.subheader("2. Danh sách sản phẩm trong PO (Nhập mã tự do & Dò giá tự động)")
    st.markdown(f"🎯 *Đang đối soát danh mục báo giá cho công ty:* **{customer_name}** *(Bạn có thể gõ bất kỳ mã nào, hệ thống sẽ kiểm tra khi tạo PO)*")

    # Lấy dữ liệu giá theo khách hàng
    df_price_filtered = st.session_state.df_price_list[
        st.session_state.df_price_list["Tên Công Ty / Khách Hàng"].str.strip().str.lower() == customer_name.strip().lower()
    ]
    
    price_dict = dict(zip(df_price_filtered["Mã SP / Quy cách"], df_price_filtered["Đơn giá chuẩn (VNĐ)"])) if not df_price_filtered.empty else {}
    unit_dict = dict(zip(df_price_filtered["Mã SP / Quy cách"], df_price_filtered["ĐVT"])) if not df_price_filtered.empty else {}

    # Chuyển cột Mã SP thành TextColumn để cho phép nhập chữ/mã bất kỳ không bị ép chọn
    edited_df = st.data_editor(
        st.session_state.df_po_items,
        num_rows="dynamic",
        use_container_width=True,
        key="po_table",
        column_config={
            "Mã SP / Quy cách": st.column_config.TextColumn(
                "Mã SP / Quy cách",
                required=True,
                help="Nhập mã sản phẩm do khách gửi (có thể gõ mã bất kỳ)"
            ),
            "ĐVT": st.column_config.SelectboxColumn(
                "Đơn vị tính",
                options=["Kg", "Thùng", "Phuy", "Lon"],
                required=True
            ),
            "Số lượng": st.column_config.NumberColumn(min_value=0.0, step=1.0, format="%,.0f"),
            "Đơn giá (VNĐ)": st.column_config.NumberColumn(min_value=0.0, step=1000.0, format="%,.0f")
        }
    )

    # Tự động load đơn giá nếu mã khớp với bảng giá của khách hàng
    for idx, row in edited_df.iterrows():
        code = str(row["Mã SP / Quy cách"]).strip()
        if code in price_dict:
            current_price = row["Đơn giá (VNĐ)"]
            if pd.isna(current_price) or current_price == 0.0 or current_price != price_dict[code]:
                edited_df.loc[idx, "Đơn giá (VNĐ)"] = price_dict[code]
            if code in unit_dict and (pd.isna(row["ĐVT"]) or row["ĐVT"] == ""):
                edited_df.loc[idx, "ĐVT"] = unit_dict[code]

    st.session_state.df_po_items = edited_df

    note = st.text_area("Ghi chú đặc biệt cho phòng kế hoạch", value="Giao gấp, kiểm tra kỹ chất lượng màu trước khi xuất kho.")

    if st.button("🚀 Tạo và Hiển thị Giao diện PO Hoàn Chỉnh", type="primary"):
        if not customer_name or not po_number or edited_df.empty:
            st.error("Vui lòng điền Tên khách hàng, Mã số PO và nhập ít nhất 1 sản phẩm!")
        else:
            # --- KIỂM TRA LỖI: RÀ SOÁT TÍNH HỢP LỆ CỦA MÃ SẢN PHẨM ---
            has_error = False
            error_messages = []

            # Lấy danh sách toàn bộ mã hợp lệ của khách hàng này
            valid_codes_for_customer = df_price_filtered["Mã SP / Quy cách"].tolist()

            for index, row in edited_df.iterrows():
                code = str(row["Mã SP / Quy cách"]).strip()
                qty = float(row["Số lượng"]) if not pd.isna(row["Số lượng"]) else 0.0
                
                if code and qty > 0:
                    # Kiểm tra nếu mã gõ vào không có trong danh mục báo giá của công ty đó
                    if code not in valid_codes_for_customer:
                        has_error = True
                        error_messages.append(f"❌ Lỗi dòng {index + 1}: Công ty **'{customer_name}'** không có báo giá cho mã sản phẩm **'{code}'**!")

            if has_error:
                for err in error_messages:
                    st.error(err)
                st.warning("⚠️ Hệ thống đã chặn tạo PO do phát hiện mã sản phẩm không hợp lệ hoặc không có báo giá cho khách hàng này!")
            else:
                items = []
                subtotal = 0.0
                
                for index, row in edited_df.iterrows():
                    code = str(row["Mã SP / Quy cách"]).strip()
                    qty = float(row["Số lượng"]) if not pd.isna(row["Số lượng"]) else 0.0
                    unit = str(row["ĐVT"])
                    price = float(row["Đơn giá (VNĐ)"]) if not pd.isna(row["Đơn giá (VNĐ)"]) else 0.0
                    
                    if code and qty > 0:
                        amount = qty * price
                        subtotal += amount
                        items.append({
                            "Mã SP / Quy cách": code,
                            "Số lượng": f"{qty:,.0f}",
                            "ĐVT": unit,
                            "Đơn giá (VNĐ)": f"{price:,.0f}",
                            "Thành tiền (VNĐ)": f"{amount:,.0f}"
                        })
                        
                vat_amount = subtotal * 0.08
                grand_total = subtotal + vat_amount
                    
                st.session_state.po_data = {
                    "customer": customer_name,
                    "po_no": po_number,
                    "order_date": order_date_str,
                    "delivery_date": delivery_date_str,
                    "sales": sales_person,
                    "items": items,
                    "subtotal": f"{subtotal:,.0f}",
                    "vat": f"{vat_amount:,.0f}",
                    "grand_total": f"{grand_total:,.0f}",
                    "note": note
                }
                st.success(f"Đã xử lý thành công đơn hàng {po_number} cho khách hàng {customer_name}!")

    # --- KHUNG HIỂN THỊ GIAO DIỆN PO CHUẨN CHỈNH ---
    if st.session_state.po_data is not None:
        data = st.session_state.po_data
        
        st.markdown("---")
        st.markdown(
            """
            <style>
            .po-container {
                border: 2px solid #ccc;
                padding: 30px;
                border-radius: 10px;
                background-color: #fafafa;
                color: #000;
                font-family: Arial, sans-serif;
            }
            .po-header {
                text-align: center;
                font-weight: bold;
                font-size: 22px;
                margin-bottom: 20px;
                color: #1f77b4;
            }
            .po-summary {
                text-align: right;
                font-size: 15px;
                line-height: 1.6;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        with st.container():
            st.markdown('<div class="po-container">', unsafe_allow_html=True)
            st.markdown('<div class="po-header">PHIẾU XÁC NHẬN ĐƠN HÀNG (PO) <br><span style="font-size:14px; color:#555;">Gửi Phòng Kế Hoạch & Tài Chính</span></div>', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Mã số PO:** {data['po_no']}")
                st.markdown(f"**Khách hàng:** {data['customer']}")
                st.markdown(f"**Ngày nhận PO:** {data['order_date']}")
            with col_b:
                st.markdown(f"**Sales phụ trách:** {data['sales']}")
                st.markdown(f"**Ngày yêu cầu giao:** {data['delivery_date']}")
                
            st.markdown("---")
            st.markdown("**Chi tiết danh sách sản phẩm / mã mực đặt hàng:**")
            
            df_display = pd.DataFrame(data['items'])
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.markdown(f"""
            <div class="po-summary">
                <b>Cộng tiền hàng:</b> {data['subtotal']} VNĐ<br>
                <b>Thuế VAT (8%):</b> {data['vat']} VNĐ<br>
                <b><span style="font-size: 18px; color: #d9534f;">Tổng cộng thanh toán (Gồm VAT):</span></b> <span style="font-size: 18px; color: #d9534f; font-weight: bold;">{data['grand_total']} VNĐ</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br><b>Ghi chú đặc biệt:</b>", unsafe_allow_html=True)
            st.info(data['note'] if data['note'] else "Không có ghi chú đặc biệt.")
            
            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("⚙️ Quản lý & Cập nhật danh mục giá theo từng Khách Hàng")
    st.markdown("Quản lý chi tiết giá bán từng mã mực theo từng công ty và thời điểm báo giá.")
    
    updated_price_list = st.data_editor(
        st.session_state.df_price_list,
        num_rows="dynamic",
        use_container_width=True,
        key="price_list_table",
        column_config={
            "Tên Công Ty / Khách Hàng": st.column_config.TextColumn("Tên Công Ty / Khách Hàng", required=True),
            "Mã SP / Quy cách": st.column_config.TextColumn("Mã SP / Quy cách", required=True),
            "ĐVT": st.column_config.SelectboxColumn("Đơn vị tính", options=["Kg", "Thùng", "Phuy", "Lon"], required=True),
            "Đơn giá chuẩn (VNĐ)": st.column_config.NumberColumn("Đơn giá chuẩn (VNĐ)", min_value=0.0, step=1000.0, format="%,.0f"),
            "Ngày Báo Giá": st.column_config.TextColumn("Ngày Báo Giá (dd/mm/yyyy)", required=True, help="Nhập định dạng dd/mm/yyyy")
        }
    )
    
    if st.button("💾 Lưu Cập Nhật Bảng Giá Khách Hàng"):
        st.session_state.df_price_list = updated_price_list
        st.success("Đã cập nhật bảng giá chi tiết theo từng khách hàng thành công!")
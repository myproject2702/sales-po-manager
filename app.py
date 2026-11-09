import os
import pandas as pd
import streamlit as st

# Cấu hình giao diện trang web
st.set_page_config(
    page_title="Hệ Thống Quản Lý PO & Định Giá", page_icon="📦", layout="wide"
)

# --- KHỞI TẠO DỮ LIỆU MẪU (Bảng giá và Khách hàng) ---
# Trong thực tế, bạn có thể thay thế hoặc đọc từ file Excel/CSV
if "price_db" not in st.session_state:
  st.session_state.price_db = pd.DataFrame({
      "Mã Khách Hàng": [
          "KH_A",
          "KH_A",
          "KH_B",
          "KH_B",
          "KH_C",
      ],
      "Tên Khách Hàng": [
          "Công ty TNHH Nhựa Miền Nam",
          "Công ty TNHH Nhựa Miền Nam",
          "Công ty CP Bao Bì Bình Minh",
          "Công ty CP Bao Bì Bình Minh",
          "Tập đoàn Nhựa Tân Tiến",
      ],
      "Mã Sản Phẩm": [
          "PE_GOLD",
          "PE_HR",
          "PE_8365",
          "PE_GOLD",
          "PE_HR",
      ],
      "Tên Sản Phẩm": [
          "Mực in PE Gold cao cấp",
          "Mực in PE(HR) chịu nhiệt",
          "Mực in PE 8365 đặc biệt",
          "Mực in PE Gold cao cấp",
          "Mực in PE(HR) chịu nhiệt",
      ],
      "Đơn Giá (VNĐ)": [150000, 140000, 155000, 148000, 142000],
  })

# --- QUẢN LÝ FILE LỊCH SỬ PO ---
HISTORY_FILE = "po_history.csv"


def load_po_history():
  if os.path.exists(HISTORY_FILE):
    return pd.read_csv(HISTORY_FILE)
  else:
    return pd.DataFrame(columns=[
        "Mã PO",
        "Khách hàng",
        "Ngày tạo",
        "Ngày giao",
        "Tổng tiền (VNĐ)",
        "Chi tiết sản phẩm",
    ])


def save_po_record(po_data):
  df_history = load_po_history()
  new_row = pd.DataFrame([po_data])
  df_history = pd.concat([df_history, new_row], ignore_index=True)
  df_history.to_csv(HISTORY_FILE, index=False)


# --- THANH BÊN (SIDEBAR) & BRANDING ---
st.sidebar.image(
    "logo.png", width=160
)  # Nhớ đưa file logo.png lên cùng thư mục GitHub
st.sidebar.title("Hệ Thống Sales PO")
st.sidebar.markdown("---")
menu_mode = st.sidebar.radio(
    "Chức năng chính:", ["Tạo & Kiểm Tra PO", "Quản Lý Bảng Giá", "Lịch Sử PO"]
)

# --- GIAO DIỆN CHÍNH ---

if menu_mode == "Tạo & Kiểm Tra PO":
  st.title("📦 Tạo Đơn Đặt Hàng (Purchase Order)")
  st.markdown(
      "Nhập thông tin đơn hàng bên dưới. Hệ thống sẽ tự động đối chiếu giá và"
      " kiểm tra mã sản phẩm theo cơ sở dữ liệu khách hàng."
  )

  col1, col2 = st.columns(2)
  with col1:
    po_number = st.text_input("Mã PO (Ví dụ: PO-2026-001)")
    # Lấy danh sách khách hàng duy nhất
    list_customers = st.session_state.price_db["Tên Khách Hàng"].unique()
    selected_customer = st.selectbox(
        "Chọn Khách Hàng", options=list_customers
    )

  with col2:
    po_date = st.date_input("Ngày tạo PO")
    delivery_date = st.date_input("Ngày giao hàng dự kiến")

  st.markdown("### Chi tiết sản phẩm đặt mua")

  # Lọc danh sách sản phẩm theo khách hàng đã chọn
  valid_products_df = st.session_state.price_db[
      st.session_state.price_db["Tên Khách Hàng"] == selected_customer
  ]

  # Tạo bảng nhập liệu sản phẩm (Data Editor cho phép nhập linh hoạt)
  if "cart_df" not in st.session_state:
    st.session_state.cart_df = pd.DataFrame(
        columns=["Mã Sản Phẩm", "Số Lượng", "Đơn Giá Thỏa Thuận"]
    )

  # Form nhập sản phẩm nhanh
  with st.form("add_item_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
      # Cho phép nhập tự do mã sản phẩm theo yêu cầu
      input_code = st.text_input(
          "Mã sản phẩm", placeholder="Nhập mã (VD: PE_GOLD)"
      )
    with c2:
      input_qty = st.number_input(
          "Số lượng", min_value=1, value=100, step=10
      )
    with c3:
      input_price = st.number_input(
          "Đơn giá đề xuất (VNĐ)", min_value=0.0, value=0.0, step=1000.0
      )

    submitted = st.form_submit_button("➕ Thêm vào đơn hàng")
    if submitted:
      if input_code:
        new_item = pd.DataFrame({
            "Mã Sản Phẩm": [input_code],
            "Số Lượng": [input_qty],
            "Đơn Giá Thỏa Thuận": [input_price],
        })
        st.session_state.cart_df = pd.concat(
            [st.session_state.cart_df, new_item], ignore_index=True
        )
        st.success(f"Đã thêm mã sản phẩm: {input_code}")
      else:
        st.warning("Vui lòng nhập mã sản phẩm!")

  # Hiển thị danh sách sản phẩm hiện tại trong giỏ hàng
  if not st.session_state.cart_df.empty:
    st.subheader("Danh sách sản phẩm trong PO hiện tại:")
    edited_cart = st.data_editor(
        st.session_state.cart_df, use_container_width=True, num_rows="dynamic"
    )
    st.session_state.cart_df = edited_cart

    if st.button("🚀 Kiểm Tra & Xác Nhận Tạo PO"):
      if not po_number:
        st.error("Vui lòng nhập Mã PO trước khi xác nhận!")
      else:
        # Kiểm tra validation mã sản phẩm chéo với database giá của khách hàng
        error_flag = False
        total_amount = 0
        validated_items = []

        for index, row in st.session_state.cart_df.iterrows():
          code = row["Mã Sản Phẩm"]
          qty = row["Số Lượng"]
          price = row["Đơn Giá Thỏa Thuận"]

          # Tra cứu trong database giá của khách hàng này
          match = valid_products_df[valid_products_df["Mã Sản Phẩm"] == code]

          if match.empty:
            st.error(
                f"❌ Lỗi: Mã sản phẩm **'{code}'** không hợp lệ hoặc không nằm"
                f" trong bảng giá đã đăng ký của khách hàng"
                f" **{selected_customer}**!"
            )
            error_flag = True
            break
          else:
            total_amount += qty * price
            validated_items.append(f"{code} (SL: {qty})")

        if not error_flag:
          st.success(
              "🎉 Tất cả mã sản phẩm hợp lệ! PO đã được tạo và lưu thành công."
          )
          st.info(f"💰 Tổng giá trị đơn hàng: **{total_amount:,.0f} VNĐ**")

          # Lưu vào lịch sử PO
          po_record = {
              "Mã PO": po_number,
              "Khách hàng": selected_customer,
              "Ngày tạo": po_date.strftime("%d/%m/%Y"),
              "Ngày giao": delivery_date.strftime("%d/%m/%Y"),
              "Tổng tiền (VNĐ)": total_amount,
              "Chi tiết sản phẩm": ", ".join(validated_items),
          }
          save_po_record(po_record)

          # Reset giỏ hàng sau khi tạo xong
          st.session_state.cart_df = pd.DataFrame(
              columns=["Mã Sản Phẩm", "Số Lượng", "Đơn Giá Thỏa Thuận"]
          )

  if st.button("🔄 Làm mới đơn hàng"):
    st.session_state.cart_df = pd.DataFrame(
        columns=["Mã Sản Phẩm", "Số Lượng", "Đơn Giá Thỏa Thuận"]
    )
    st.rerun()

elif menu_mode == "Quản Lý Bảng Giá":
  st.title("📋 Quản Lý Bảng Giá Khách Hàng")
  st.markdown(
      "Dưới đây là cơ sở dữ liệu giá chuẩn đang áp dụng cho từng khách hàng:"
  )

  # Cho phép chỉnh sửa trực tiếp bảng giá trên giao diện
  edited_price_db = st.data_editor(
      st.session_state.price_db, use_container_width=True, num_rows="dynamic"
  )
  st.session_state.price_db = edited_price_db
  st.success("Mọi thay đổi trong bảng giá sẽ được áp dụng ngay lập tức.")

elif menu_mode == "Lịch Sử PO":
  st.title("📜 Tra Cứu Lịch Sử Đơn Hàng (PO)")
  st.markdown("Xem lại toàn bộ danh sách các đơn hàng đã được tạo trước đó.")

  df_history = load_po_history()

  if df_history.empty:
    st.info("Chưa có lịch sử đơn hàng nào được tạo.")
  else:
    # Tìm kiếm nhanh
    search_query = st.text_input(
        "🔍 Nhập Mã PO hoặc tên khách hàng để tìm kiếm:"
    )

    if search_query:
      filtered_df = df_history[
          df_history["Mã PO"]
          .astype(str)
          .str.contains(search_query, case=False, na=False)
          | df_history["Khách hàng"]
          .astype(str)
          .str.contains(search_query, case=False, na=False)
      ]
    else:
      filtered_df = df_history

    st.dataframe(filtered_df, use_container_width=True)

    # Nút tải xuống file CSV lịch sử
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Tải xuống danh sách lịch sử (CSV)",
        data=csv_data,
        file_name="lich_su_po_doanh_nghiep.csv",
        mime="text/csv",
    )

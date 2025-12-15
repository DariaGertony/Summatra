import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import json

st.set_page_config(
    page_title="Meme Manager",
    layout="wide"
)


API_BASE_URL = "http://dbworker:3434"

@st.cache_data(ttl=300)
def cached_get_all_items():
    return get_all_items()

@st.cache_data(ttl=300)
def cached_get_by_tag(tag):
    return get_by_tag(tag)

@st.cache_data(ttl=300)
def cached_get_by_name(name):
    return get_by_name(name)

@st.cache_data(ttl=300)
def cached_get_by_id(meme_id):
    return get_by_id(meme_id)

@st.cache_data(ttl=300)
def ask_about(mem_source, image):
    try:
        files = {'image': image, "source": mem_source}
        response = requests.post('http://talker:3456/memmer', json=files, timeout=100)
        if response.status_code == 200:
            return response.json().get("summary", [])
        return ''
    except Exception as e:
        st.error(f"Ошибка подключения: {str(e)}")
        return ''



st.title("Meme Manager")
st.markdown("---")

def get_all_items():
    try:
        response = requests.get(f"{API_BASE_URL}/items", timeout=10)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
    except Exception as e:
        st.error(f"Ошибка подключения: {str(e)}")
        return []

def get_by_tag(tag):
    try:
        response = requests.get(f"{API_BASE_URL}/tag/{tag}", timeout=10)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
    except:
        return []

def get_by_name(name):
    try:
        response = requests.get(f"{API_BASE_URL}/name/{name}", timeout=10)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
    except:
        return []

def get_by_id(meme_id):
    try:
        response = requests.get(f"{API_BASE_URL}/id/{meme_id}", timeout=10)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
    except:
        return []

def add_meme(name, data, tags):
    try:
        payload = {
            "name": name,
            "data": data,
            "tags": tags
        }
        response = requests.post(f"{API_BASE_URL}/addmeme", json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False


with st.sidebar:
    st.title("Навигация")
    if st.button("Обновить все данные"):
        st.cache_data.clear()
        st.rerun()
        
    st.markdown("---")
    st.markdown("### Быстрый поиск")
    quick_search = st.text_input("Поиск ID", placeholder="Введите ID мема")
    if quick_search:
        results = cached_get_by_id(quick_search)
        if results:
            for item in results:
                st.write(f"**Название:** {item[0]}")
                if item[1]:  
                    try:
                        img_bytes = base64.b64decode(item[1])
                        image = Image.open(BytesIO(img_bytes))
                        st.image(image, caption=f"ID: {quick_search}", width=200)
                    except:
                        st.write("Изображение не загружено")
        else:
            st.write("Мем не найден")
    
    st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Все мемы", "Добавить", "Поиск", "Спросить про мем"])


with tab1:
    st.header("Все мемы")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        tag_filter = st.text_input("Фильтр по тегу", placeholder="Введите тег")
    
    
    items = cached_get_all_items() 
    
    if not items:
        st.info("В базе нет мемов")
    else:
        if tag_filter:
            filtered_items = []
            for item in items:
                if tag_filter in [item[2], item[3], item[4]]:
                    filtered_items.append(item)
            items = filtered_items
        
        
        st.markdown("### Список мемов")
        for idx, item in enumerate(items):
            meme_id, name, tag1, tag2, tag3 = item
            
            with st.container(border=True):
                col_left, col_right = st.columns([1, 3])
                
                with col_left:
                    image_data = get_by_id(meme_id)
                    if image_data and len(image_data) > 0 and len(image_data[0]) > 1:
                        try:
                            img_bytes = base64.b64decode(image_data[0][1])
                            image = Image.open(BytesIO(img_bytes))
                            st.image(image, width=200)
                        except Exception as e:
                            st.warning(f"Неверный формат {e}")
                    else:
                        st.info("Нет изображения")
                
                with col_right:
                    st.markdown(f"**ID:** `{meme_id}`")
                    st.markdown(f"**Название:** {name}")
                    
                    tags_html = ""
                    for tag in [tag1, tag2, tag3]:
                        if tag:
                            tags_html += f'<span style="background-color:#e0e0e0;padding:2px 8px;margin:2px;border-radius:10px;">{tag}</span> '
                    if tags_html:
                        st.markdown(f"**Теги:** {tags_html}", unsafe_allow_html=True)
                    



with tab2:
    st.header("Добавить новый мем")
    with st.form("add_meme_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            meme_name = st.text_input("Название мема *", max_chars=100)
            uploaded_file = st.file_uploader(
                "Изображение *", 
                type=['png', 'jpg', 'jpeg']
            )
        
        with col2:
            tags = []
            tags.append(st.text_input("Тег 1", max_chars=20, key="tag1"))
            tags.append(st.text_input("Тег 2", max_chars=20, key="tag2"))
            tags.append(st.text_input("Тег 3", max_chars=20, key="tag3"))

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Предпросмотр", width=300)
        
        submitted = st.form_submit_button("Сохранить мем", type="primary")
        
        if submitted:
            if not meme_name or not uploaded_file:
                st.error("Заполните поля")
            else:
                buffered = BytesIO()
                image_format = "JPEG" if uploaded_file.type in ["image/jpeg", "image/jpg"] else "PNG"
                image.save(buffered, format=image_format)
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                if add_meme(meme_name, img_base64, tags):
                    st.success("Мем успешно сохранен")
                else:
                    st.error("Ошибка при сохранении")
with tab4:
    st.header("Спросить новый мем")
    if "asked_answer" not in st.session_state:
        with st.form("ask_meme_form", clear_on_submit=True):
            meme_name = st.text_input("Источник мема *", max_chars=100)
            uploaded_file = st.file_uploader(
                "Изображение *", 
                type=['png', 'jpg', 'jpeg']
            )
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Предпросмотр", width=300)
            
            submitted = st.form_submit_button("Спросить про мем", type="primary")
            
            if submitted:
                if not meme_name or not uploaded_file:
                    st.error("Заполните поля")
                else:
                    buffered = BytesIO()
                    image_format = "JPEG" if uploaded_file.type in ["image/jpeg", "image/jpg"] else "PNG"
                    image.save(buffered, format=image_format)
                    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    answer = ask_about(meme_name, img_base64)
                    
                    if answer:
                        st.session_state.asked_answer = answer
                        st.session_state.uploaded_image = uploaded_file
                        st.session_state.image_bytes = buffered.getvalue()
                        st.session_state.image_format = image_format
                        st.rerun()
                    else:
                        st.error("Ошибка при запросе")

    else:
        st.success(f"**Ответ:** {st.session_state.asked_answer}")
        memename = st.text_input("Назовите мем", max_chars=100, key="memename_input")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Сохранить мем", type="primary"):
                if memename.strip():
                    # Берём данные из сессии
                    img_base64 = base64.b64encode(st.session_state.image_bytes).decode('utf-8')
                    tags = st.session_state.asked_answer.split("|")[1:4]
                    
                    if add_meme(memename, img_base64, tags):
                        st.success("Мем сохранён")
                        del st.session_state.asked_answer
                        del st.session_state.uploaded_image
                        del st.session_state.image_bytes
                        del st.session_state.image_format
                        st.rerun()
                    else:
                        st.error("Ошибка при сохранении")
                else:
                    st.warning("Введите название мема")
        
        with col2:
            if st.button("Заново"):
                # Сброс
                del st.session_state.asked_answer
                del st.session_state.uploaded_image
                del st.session_state.image_bytes
                del st.session_state.image_format
                st.rerun()


with tab3:
    st.header("Поиск мемов")
    
    search_type = st.radio("Тип поиска", ["По тегу", "По названию", "По ID"], horizontal=True)
    
    if search_type == "По тегу":
        tag = st.text_input("Введите тег")
        if tag:
            items = cached_get_by_tag(tag)
    
    elif search_type == "По названию":
        name = st.text_input("Введите название")
        if name:
            items = cached_get_by_name(name)
    else: 
        meme_id = st.text_input("Введите ID")
        if meme_id:
            items = cached_get_by_id(meme_id)
    
    if 'items' in locals() and items:
        st.success(f"Найдено: {len(items)} мемов")
        
        for item in items:
            if search_type == "По ID":
                name, data = item[0], item[1] if len(item) > 1 else None
                with st.container(border=True):
                    st.markdown(f"**Название:** {name}")
                    if data:
                        try:
                            img_bytes = base64.b64decode(data)
                            image = Image.open(BytesIO(img_bytes))
                            st.image(image, caption=name, width=300)
                        except:
                            st.warning("Не удалось загрузить изображение")
            else:
                meme_id, name, tag1, tag2, tag3 = item
                with st.container(border=True):
                    st.markdown(f"**ID:** `{meme_id}`")
                    st.markdown(f"**Название:** {name}")
                    st.markdown(f"**Теги:** {tag1 or ''} {tag2 or ''} {tag3 or ''}")

                    if st.button("Показать изображение", key=f"view_{meme_id}"):
                        image_data = cached_get_by_id(meme_id)
                        if image_data and len(image_data) > 0 and len(image_data[0]) > 1:
                            try:
                                img_bytes = base64.b64decode(image_data[0][1])
                                image = Image.open(BytesIO(img_bytes))
                                st.image(image, caption=f"{name} (ID: {meme_id})", width=400)
                            except:
                                st.error("Ошибка загрузки изображения")
                        else:
                            st.warning("Изображение не найдено")
    
    elif 'items' in locals():
        st.info("Ничего не найдено")

st.markdown("---")
st.caption("Summatra")

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #e6f7ff;
        border-bottom: 2px solid #0068c9;
    }
</style>
""", unsafe_allow_html=True)


# === PicToPoem 백엔드 서버 ===
# 이 파일은 Flask 기반의 웹 서버로, 이미지를 분석하여 문학 작품의 한 구절을 추천하는 API를 제공합니다.

import os
import google.generativeai as genai
import json
from google.generativeai.types import GenerationConfig
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import io
from PIL import Image, ImageDraw, ImageFont
from flask import send_file
from PIL import ImageFilter # Added for blur effect

# 환경변수 로드 (.env 파일에서 API 키 등을 불러옴)
load_dotenv()

# Flask 애플리케이션 초기화
# static_folder와 template_folder를 frontend 디렉토리로 설정
app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')

# Google Gemini AI API 설정
try:
    # 환경변수에서 API 키를 가져와 Gemini AI를 초기화
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    # Gemini 1.5 Flash 모델 사용 (빠르고 효율적인 모델)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except KeyError:
    print("오류: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    exit()
except Exception as e:
    print(f"API 설정 중 오류 발생: {e}")
    exit()

def text_wrap(text, font, max_width):
    """
    텍스트 자동 줄바꿈 함수
    긴 텍스트를 지정된 너비에 맞게 여러 줄로 나누어 반환합니다.
    
    Args:
        text (str): 줄바꿈할 텍스트
        font: PIL 폰트 객체
        max_width (int): 최대 너비 (픽셀)
    
    Returns:
        list: 줄바꿈된 텍스트 라인들의 리스트
    """
    lines = []
    
    # 텍스트가 비어있으면 빈 리스트 반환
    if not text:
        return lines
    
    # 텍스트가 최대 너비보다 작으면 그대로 반환
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]  # 실제 텍스트 너비 계산
    
    if text_width <= max_width:
        lines.append(text)
    else:
        # 단어 단위로 분리하여 줄바꿈 처리
        words = text.split(' ')
        current_line = ''
        
        for word in words:
            # 현재 줄에 단어를 추가했을 때의 너비 계산
            test_line = current_line + word + " "
            test_bbox = font.getbbox(test_line)
            test_width = test_bbox[2] - test_bbox[0]
            
            if test_width <= max_width:
                # 단어를 현재 줄에 추가
                current_line = test_line
            else:
                # 현재 줄이 비어있지 않으면 줄바꿈
                if current_line:
                    lines.append(current_line.strip())
                    current_line = word + " "
                else:
                    # 단어가 너무 길어서 줄바꿈이 필요한 경우
                    # 단어를 여러 줄로 나누기
                    for char in word:
                        test_line = current_line + char
                        test_bbox = font.getbbox(test_line)
                        test_width = test_bbox[2] - test_bbox[0]
                        
                        if test_width <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line.strip())
                                current_line = char
                            else:
                                current_line = char
                    current_line += " "
        
        # 마지막 줄 추가
        if current_line:
            lines.append(current_line.strip())
    
    return lines

# === 웹 라우트 정의 ===

@app.route('/')
def index():
    """
    메인 페이지 라우트
    사용자가 이미지를 업로드할 수 있는 웹 페이지를 반환합니다.
    """
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_quote():
    """
    이미지 분석 및 문학 작품 추천 API
    업로드된 이미지를 분석하여 어울리는 문학 작품의 한 구절을 추천합니다.
    
    Returns:
        JSON: 추천된 문학 작품 정보 (인용구, 출처, 해설)
    """
    # 이미지 파일이 요청에 포함되어 있는지 확인
    if 'image' not in request.files:
        return jsonify({'error': '이미지 파일이 없습니다.'}), 400

    image_file = request.files['image']

    # 파일이 실제로 선택되었는지 확인
    if image_file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400

    try:
        # 이미지 파일을 바이트로 읽기
        img_bytes = image_file.read()
        
        # Gemini AI에 전달할 이미지 데이터 형식
        image_part = {
            "mime_type": image_file.mimetype,
            "data": img_bytes
        }

        # AI에게 전달할 프롬프트 (문학 큐레이터 역할 정의)
        prompt_text = """
        <role>
        당신은 세계 문학에 정통한 문학 큐레이터이자 감성적인 작가입니다. 당신의 임무는 주어진 이미지에 가장 깊은 영감을 주는 '실존하는' 문학 작품의 한 문단을 찾아, 그 이유를 설명하는 것입니다. 당신의 모든 정보는 사실에 기반해야 합니다.
        </role>

        <instructions>
        주어진 이미지를 분석하고 다음 단계를 엄격하게 따르세요:
        1.  **이미지 분석:** 이미지의 핵심 사물, 분위기, 색감, 그리고 전체적인 감정선을 파악합니다.
        2.  **문학 작품 탐색:** 분석된 감정선을 바탕으로, '실존하며 검증 가능한' 전 세계의 문학 작품을 탐색합니다. **절대로 작가, 작품, 인용구를 지어내서는 안 됩니다.**
        3.  **문단 선택:** 작품 속에서 이미지의 감성을 가장 잘 함축하고 있는 하나의 완성된 문단을 그대로 인용합니다.
        4.  **사실 검증 (Fact-Check):** 선택한 문단과 출처(작가, 작품명)가 실제로 존재하는지 다시 한번 확인합니다. 불확실하거나 가상의 정보는 절대 포함하지 마세요.
        5.  **해설 작성:** 왜 이 문단을 선택했는지, 문단의 어떤 부분이 이미지의 어떤 요소와 조응하는지를 설명하는 '큐레이터의 해설'을 작성합니다.
        </rules>

        <output_format>
        결과는 아래의 JSON 형식을 반드시 준수하여 다른 어떤 설명도 없이 오직 JSON 데이터만 출력하세요. JSON 코드 블록 마크업도 사용하지 마세요.
        {
          "quote": "인용한 문단",
          "source": {
            "title": "작품명",
            "author": "작가"
          },
          "commentary": "큐레이터의 해설"
        }
        </output_format>
        """

        # AI 생성 설정 (temperature=0.2로 일관된 결과 생성)
        generation_config = GenerationConfig(temperature=0.2)

        # Gemini AI에 이미지와 프롬프트 전달하여 응답 생성
        response = model.generate_content([prompt_text, image_part], generation_config=generation_config)
        raw_text = response.text

        # AI 응답에서 JSON 부분만 추출하여 파싱
        try:
            json_start_index = raw_text.find('{')
            json_end_index = raw_text.rfind('}') + 1
            
            if json_start_index != -1 and json_end_index != -1:
                json_string = raw_text[json_start_index:json_end_index]
                result_json = json.loads(json_string)
            else:
                raise ValueError("Valid JSON object not found in the response.")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse JSON from response. Error: {e}")
            print(f"Original AI Response: {raw_text}")
            return jsonify({'error': 'AI 응답 형식이 잘못되었습니다.'}), 500
        
        # 성공적으로 파싱된 결과를 JSON으로 반환
        return jsonify(result_json)

    except Exception as e:
        print(f"API 호출 오류: {e}")
        return jsonify({'error': '글귀를 생성하는 데 실패했습니다. 서버 로그를 확인하세요.'}), 500

@app.route('/api/create-story', methods=['POST'])
def create_story_image():
    """
    스토리 이미지 생성 API
    AI가 디자인 결정을 내리고 PIL로 아름다운 스토리 이미지를 생성합니다.
    
    Returns:
        PNG 이미지 파일: AI가 디자인한 스토리 이미지
    """
    print("=== AI 디자인 스토리 이미지 생성 시작 ===")
    
    # 이미지 파일 확인
    if 'image' not in request.files:
        print("오류: 이미지 파일이 없습니다.")
        return jsonify({'error': '이미지 파일이 없습니다.'}), 400

    original_image_file = request.files['image']
    quote = request.form.get('quote', '')  # 인용구
    author = request.form.get('author', '')  # 작가
    title = request.form.get('title', '')  # 작품명
    
    print(f"받은 데이터: quote='{quote[:50]}...', author='{author}', title='{title}'")

    try:
        # 이미지 파일을 바이트로 읽기
        img_bytes = original_image_file.read()
        
        # Gemini AI에 전달할 이미지 데이터 형식
        image_part = {
            "mime_type": original_image_file.mimetype,
            "data": img_bytes
        }

        # AI에게 전달할 프롬프트 (디자인 결정 요청)
        design_prompt = f"""
        <role>
        당신은 전문적인 그래픽 디자이너입니다. 주어진 이미지와 문학 작품을 분석하여 최적의 디자인 결정을 내려주세요.
        </role>

        <task>
        인스타그램 스토리(1080x1920)에 최적화된 디자인을 결정하세요.

        <layout_requirements>
        - 순서: 이미지 → 글귀 → 작가 및 제목 (세로 배치)
        - 오버랩 금지: 이미지와 텍스트가 겹치지 않도록 배치
        - 모든 요소는 템플릿을 벗어나지 않도록 배치
        </layout_requirements>

        <content>
        인용구: "{quote}" ({len(quote)}자)
        출처: "{author}, 「{title}」"
        </content>

        <constraints>
        - 폰트 색상: 흰색 또는 검은색만 사용
        - 크기: 인스타그램 스토리 크기(1080x1920) 준수
        - 배경: 단색 배경만 사용
        </constraints>

        <output_format>
        다음 JSON 형식으로 응답해주세요:
        {{
          "background_color": [R, G, B],
          "text_color": "white" 또는 "black",
          "quote_size": 40-80,
          "source_size": 30-50,
          "line_spacing": 15-35
        }}
        </output_format>
        </task>
        """

        # AI 생성 설정
        generation_config = GenerationConfig(temperature=0.7)

        # Gemini AI에 이미지와 디자인 프롬프트 전달
        print("AI 디자인 분석 중...")
        response = model.generate_content([design_prompt, image_part], generation_config=generation_config)
        
        # AI 응답에서 JSON 추출
        try:
            json_start_index = response.text.find('{')
            json_end_index = response.text.rfind('}') + 1
            
            if json_start_index != -1 and json_end_index != -1:
                json_string = response.text[json_start_index:json_end_index]
                design_config = json.loads(json_string)
                print("AI 디자인 설정 추출 완료")
            else:
                raise ValueError("Valid JSON object not found in the response.")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"AI 디자인 설정 파싱 실패: {e}")
            print(f"AI 응답: {response.text}")
            # 기본 설정 사용
            design_config = get_default_design_config()
        
        # AI 디자인 설정으로 이미지 생성
        return create_ai_designed_image(original_image_file, quote, author, title, design_config)

    except Exception as e:
        print(f"AI 디자인 분석 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'AI 디자인 분석에 실패했습니다.'}), 500

def get_default_design_config():
    """기본 디자인 설정"""
    return {
        "background_color": [25, 25, 25],
        "text_color": "white",
        "quote_size": 60,
        "source_size": 40,
        "line_spacing": 25
    }

def create_ai_designed_image(image_file, quote, author, title, design_config):
    """AI 디자인 설정으로 이미지 생성"""
    try:
        print("=== 스토리 이미지 생성 시작 ===")
        
        # 인스타그램 스토리 크기 (1080x1920) 준수
        story_bg = Image.new('RGB', (1080, 1920), color=tuple(design_config.get("background_color", [25, 25, 25])))
        print("✓ 배경 이미지 생성 완료")
        
        # 원본 이미지 처리
        user_img = Image.open(image_file.stream).convert("RGBA")
        
        # 이미지 크기 정보 가져오기
        img_width, img_height = user_img.size
        
        # 이미지가 너무 크면 적절한 크기로 조정 (최대 900px)
        max_size = 900
        if img_width > max_size or img_height > max_size:
            user_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            img_width, img_height = user_img.size
            print(f"✓ 이미지 크기 조정 완료: {img_width}x{img_height}")
        else:
            print(f"✓ 이미지 크기 확인: {img_width}x{img_height}")
        
        # 텍스트 그리기
        draw = ImageDraw.Draw(story_bg)
        
        # 폰트 로드
        font_path = os.path.join(os.path.dirname(__file__), "Gyeong-gi_Regular.ttf")
        try:
            quote_font = ImageFont.truetype(font_path, design_config.get("quote_size", 60))
            source_font = ImageFont.truetype(font_path, design_config.get("source_size", 40))
            print("✓ 폰트 로드 완료")
        except:
            quote_font = ImageFont.load_default()
            source_font = ImageFont.load_default()
            print("✓ 기본 폰트 사용")
        
        # 텍스트 색상 결정 (흰색 또는 검은색)
        text_color = (255, 255, 255) if design_config.get("text_color", "white") == "white" else (0, 0, 0)
        print(f"✓ 텍스트 색상 설정: {design_config.get('text_color', 'white')}")
        
        # 인용구 텍스트 처리
        wrapped_quote = text_wrap(quote, quote_font, img_width)  # 이미지 너비에 맞춰 텍스트 줄바꿈
        line_spacing = design_config.get("line_spacing", 25)
        print(f"✓ 텍스트 줄바꿈 완료: {len(wrapped_quote)}줄")
        
        # 출처 텍스트
        source_text = f"– {author}, 「{title}」"
        source_bbox = source_font.getbbox(source_text)
        source_width = source_bbox[2] - source_bbox[0]
        source_height = source_bbox[3] - source_bbox[1]
        
        # 각 컴포넌트의 높이 계산
        quote_height = 0
        for line in wrapped_quote:
            bbox = quote_font.getbbox(line)
            quote_height += bbox[3] - bbox[1] + line_spacing
        quote_height -= line_spacing  # 마지막 줄의 여백 제거
        
        print(f"✓ 컴포넌트 높이 계산 완료: 이미지={img_height}, 글귀={quote_height}, 출처={source_height}")
        
        # 프로그램이 명시적으로 Y좌표 계산
        y_coordinates = calculate_y_coordinates(img_height, quote_height, source_height)
        img_y, quote_y, source_y = y_coordinates
        
        print(f"✓ Y좌표 계산 완료: 이미지={img_y}, 글귀={quote_y}, 출처={source_y}")
        
        # 1. 이미지 배치
        img_x = int((1080 - img_width) / 2)  # 가로 중앙
        story_bg.paste(user_img, (img_x, img_y), user_img)
        print("✓ 이미지 배치 완료")
        
        # 2. 인용구 배치
        current_quote_y = quote_y
        for i, line in enumerate(wrapped_quote):
            bbox = quote_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 중앙 정렬
            x_pos = int((1080 - text_width) / 2)
            
            # 텍스트 그리기
            draw.text((x_pos, current_quote_y), line, font=quote_font, fill=text_color)
            current_quote_y += text_height + line_spacing
        print("✓ 인용구 배치 완료")
        
        # 3. 출처 텍스트 배치
        source_x = int((1080 - source_width) / 2)
        draw.text((source_x, source_y), source_text, font=source_font, fill=text_color)
        print("✓ 출처 텍스트 배치 완료")
        
        # 완성된 이미지 반환
        img_io = io.BytesIO()
        story_bg.save(img_io, 'PNG')
        img_io.seek(0)
        
        print("=== 스토리 이미지 생성 완료 ===")
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='ai_designed_story.png')
        
    except Exception as e:
        print(f"❌ 스토리 이미지 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'AI 디자인 이미지 생성에 실패했습니다.'}), 500

def calculate_y_coordinates(img_height, quote_height, source_height):
    """대칭적이고 동일 간격으로 Y좌표 계산"""
    # 화면 높이
    screen_height = 1920
    
    # 여백 설정 (상하 대칭)
    margin = 100
    
    # 사용 가능한 공간 계산
    available_height = screen_height - (2 * margin)
    
    # 각 컴포넌트 높이 합계
    total_components_height = img_height + quote_height + source_height
    
    # 동일 간격 계산
    if total_components_height > available_height:
        # 컴포넌트가 너무 클 경우 간격을 최소화
        spacing = 50
    else:
        # 동일 간격으로 배치
        spacing = (available_height - total_components_height) // 4  # 3개 컴포넌트 사이 4개 간격
    
    # Y좌표 계산 (대칭적 배치)
    start_y = margin + spacing
    
    img_y = start_y
    quote_y = img_y + img_height + spacing
    source_y = quote_y + quote_height + spacing
    
    # 오버랩 방지 및 템플릿 범위 확인
    img_bottom = img_y + img_height
    quote_bottom = quote_y + quote_height
    source_bottom = source_y + source_height
    
    # 템플릿을 벗어나지 않도록 조정
    if source_bottom > screen_height - margin:
        # 전체를 위로 이동
        excess = source_bottom - (screen_height - margin)
        img_y -= excess
        quote_y -= excess
        source_y -= excess
    
    # 최소 여백 보장
    if img_y < margin:
        img_y = margin
        quote_y = img_y + img_height + spacing
        source_y = quote_y + quote_height + spacing
    
    return img_y, quote_y, source_y

# === 애플리케이션 실행 ===
if __name__ == '__main__':
    # 개발 모드로 Flask 서버 실행 (디버그 모드 활성화)
    app.run(debug=True)
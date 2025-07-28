import os
import google.generativeai as genai
import json
from google.generativeai.types import GenerationConfig
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')

try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except KeyError:
    print("오류: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    exit()
except Exception as e:
    print(f"API 설정 중 오류 발생: {e}")
    exit()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_quote():
    if 'image' not in request.files:
        return jsonify({'error': '이미지 파일이 없습니다.'}), 400

    image_file = request.files['image']

    if image_file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400

    try:
        img_bytes = image_file.read()
        
        image_part = {
            "mime_type": image_file.mimetype,
            "data": img_bytes
        }

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

        generation_config = GenerationConfig(temperature=0.2)

        response = model.generate_content([prompt_text, image_part], generation_config=generation_config)
        raw_text = response.text

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
        
        return jsonify(result_json)

    except Exception as e:
        print(f"API 호출 오류: {e}")
        return jsonify({'error': '글귀를 생성하는 데 실패했습니다. 서버 로그를 확인하세요.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
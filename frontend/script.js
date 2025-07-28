document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const imageInput = document.getElementById('image-input');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const submitButton = document.getElementById('submit-button');
    const loadingDiv = document.getElementById('loading');
    const resultContainer = document.getElementById('result-container');
    const resultQuote = document.getElementById('result-quote');

    // 이미지 선택 시 미리보기 기능
    imageInput.addEventListener('change', () => {
        const file = imageInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreviewContainer.classList.remove('hidden');
                submitButton.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });

    // 폼 제출(글귀 생성) 시 이벤트 처리
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // 폼의 기본 제출 동작 방지

        const file = imageInput.files[0];
        if (!file) {
            alert('이미지를 선택해주세요.');
            return;
        }

        // 로딩 화면 표시, 결과 숨기기
        loadingDiv.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        submitButton.disabled = true;
        submitButton.textContent = '생성 중...';

        const formData = new FormData();
        formData.append('image', file);

        try {
            // 백엔드 API에 이미지 전송
            const response = await fetch('/api/generate', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '서버에서 오류가 발생했습니다.');
            }

            const data = await response.json();
            
            // 결과 표시
            const resultQuoteElem = document.getElementById('result-quote');
            const resultSourceElem = document.getElementById('result-source');
            const resultCommentaryElem = document.getElementById('result-commentary');

            // 받아온 데이터로 각 요소의 내용 채우기
            resultQuoteElem.textContent = data.quote;
            resultSourceElem.textContent = `— ${data.source.author}, 「${data.source.title}」`;
            resultCommentaryElem.textContent = data.commentary;

            resultContainer.classList.remove('hidden');

        } catch (error) {
            alert(`오류 발생: ${error.message}`);
            resultQuote.textContent = '글귀를 가져오는 데 실패했습니다.';
            resultContainer.classList.remove('hidden');
        } finally {
            // 로딩 화면 숨기기 및 버튼 활성화
            loadingDiv.classList.add('hidden');
            submitButton.disabled = false;
            submitButton.textContent = '글귀 생성하기';
        }
    });
});
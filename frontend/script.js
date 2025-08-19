// === PicToPoem 프론트엔드 JavaScript ===
// 이 파일은 웹 페이지의 상호작용을 담당하는 JavaScript 코드입니다.

// === 전역 변수 ===
let currentResultData = null;  // 현재 결과 데이터를 저장할 변수
let originalImageFile = null;  // 원본 이미지 파일을 저장할 변수
let shareButton = null;        // 공유 버튼 참조

// DOM이 완전히 로드된 후 실행되는 메인 함수
document.addEventListener('DOMContentLoaded', () => {
    // === DOM 요소 참조 ===
    const uploadForm = document.getElementById('upload-form');           // 업로드 폼
    const imageInput = document.getElementById('image-input');          // 파일 입력 요소
    const imagePreviewContainer = document.getElementById('image-preview-container');  // 이미지 미리보기 컨테이너
    const imagePreview = document.getElementById('image-preview');      // 이미지 미리보기 요소
    const submitButton = document.getElementById('submit-button');      // 제출 버튼
    const loadingDiv = document.getElementById('loading');             // 로딩 표시 영역
    const resultContainer = document.getElementById('result-container'); // 결과 표시 영역
    const resultQuote = document.getElementById('result-quote');        // 결과 인용구
    shareButton = document.getElementById('share-button');        // 공유 버튼 (전역 변수에 할당)
    
    // === 이미지 선택 이벤트 핸들러 ===
    imageInput.addEventListener('change', () => {
        const file = imageInput.files[0];
        if (file) {
            originalImageFile = file; // 원본 이미지 파일 저장
            
            // FileReader를 사용하여 이미지 미리보기 생성
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreviewContainer.classList.remove('hidden');  // 미리보기 표시
                submitButton.classList.remove('hidden');          // 제출 버튼 표시
            };
            reader.readAsDataURL(file);
        }
    });

    // === 폼 제출(글귀 생성) 이벤트 핸들러 ===
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // 기본 폼 제출 동작 방지
        
        // 이미지가 선택되었는지 확인
        if (!originalImageFile) {
            alert('이미지를 선택해주세요.');
            return;
        }
    
        // === UI 상태 초기화 ===
        loadingDiv.classList.remove('hidden');        // 로딩 표시 시작
        resultContainer.classList.add('hidden');      // 이전 결과 숨김
        shareButton.classList.add('hidden');          // 공유 버튼 숨김
        submitButton.disabled = true;                 // 버튼 비활성화
        submitButton.textContent = '생성 중...';      // 버튼 텍스트 변경
    
        // FormData 객체 생성하여 이미지 파일 준비
        const formData = new FormData();
        formData.append('image', originalImageFile);
    
        try {
            // === 글귀 생성 API 호출 ===
            const response = await fetch('/api/generate', {
                method: 'POST',
                body: formData,
            });
    
            // 응답 상태 확인
            if (!response.ok) {
                // 서버에서 보낸 오류 메시지를 사용하거나 기본 메시지 표시
                const errorData = await response.json().catch(() => ({ error: '서버 응답 오류' }));
                throw new Error(errorData.error);
            }
            
            // JSON 응답 파싱
            const data = await response.json();
            currentResultData = data; // 나중에 공유하기 위해 결과 데이터 저장
    
            // === DOM 요소에 결과 데이터 채우기 ===
            const resultQuoteElem = document.getElementById('result-quote');
            const resultSourceElem = document.getElementById('result-source');
            const resultCommentaryElem = document.getElementById('result-commentary');
    
            resultQuoteElem.textContent = data.quote;  // 인용구 설정
            resultSourceElem.textContent = `— ${data.source.author}, 「${data.source.title}」`;  // 출처 설정
            resultCommentaryElem.textContent = data.commentary;  // 해설 설정
    
            // === 결과 및 공유 버튼 표시 ===
            resultContainer.classList.remove('hidden');
            shareButton.classList.remove('hidden');
    
        } catch (error) {
            // 오류 발생 시 사용자에게 알림
            alert(`오류 발생: ${error.message}`);
        } finally {
            // === UI 상태 원상 복구 ===
            loadingDiv.classList.add('hidden');       // 로딩 표시 종료
            submitButton.disabled = false;            // 버튼 활성화
            submitButton.textContent = '글귀 생성하기'; // 버튼 텍스트 복구
        }
    });

    // === 스토리 이미지 생성 이벤트 핸들러 ===
    shareButton.addEventListener('click', async () => {
        // 필요한 데이터가 있는지 확인
        if (!originalImageFile || !currentResultData) {
            alert('공유할 데이터가 없습니다.');
            return;
        }

        // === 로딩 상태 시작 ===
        loadingDiv.classList.remove('hidden');
        loadingDiv.querySelector('p').textContent = '아름다운 스토리 이미지를 디자인하고 있어요...';
        shareButton.disabled = true;
        shareButton.textContent = '이미지 생성 중...';

        // === 스토리 이미지 생성 요청 데이터 준비 ===
        const formData = new FormData();
        formData.append('image', originalImageFile);
        formData.append('quote', currentResultData.quote);
        formData.append('author', currentResultData.source.author);
        formData.append('title', currentResultData.source.title);

        try {
            // === 스토리 이미지 생성 API 호출 ===
            const response = await fetch('/api/create-story', {
                method: 'POST',
                body: formData,
            });

            // 응답 상태 확인
            if (!response.ok) throw new Error('스토리 이미지 생성에 실패했습니다.');

            // === 이미지 다운로드 처리 ===
            const imageBlob = await response.blob();
            const downloadUrl = URL.createObjectURL(imageBlob);

            // 임시 다운로드 링크 생성 및 클릭
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = 'picture_to_poetry_story.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            // 메모리 정리
            URL.revokeObjectURL(downloadUrl);

        } catch (error) {
            // 오류 발생 시 사용자에게 알림
            alert(error.message);
        } finally {
            // === 로딩 상태 종료 ===
            loadingDiv.classList.add('hidden');
            shareButton.disabled = false;
            shareButton.textContent = '스토리 이미지로 저장';
        }
    });
});
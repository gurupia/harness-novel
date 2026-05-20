/**
 * apply_readability.js v2.0
 * 웹소설 모바일 가독성 최적화 도구 (하네스 설정 수호 규칙 탑재)
 *
 * Usage:
 *   단일 파일: node apply_readability.js <filepath.md>
 *   배치 모드: node apply_readability.js --batch <folder_path>
 */

const fs = require('fs');
const path = require('path');

// ─────────────────────────────────────────────
// ⚙️  설정 상수
// ─────────────────────────────────────────────

/** 모바일 단일 문단 최대 글자 수 기준. 이 이상이면 분리. */
const MOBILE_PARA_THRESHOLD = 140;

/** 의성어/효과음 라인 판정 최대 길이 */
const SOUND_EFFECT_MAX_LEN = 50;

// ─────────────────────────────────────────────
// 🛡️  보호 판정 함수들
// ─────────────────────────────────────────────

/**
 * 장면 구분선(* * *) 보호
 */
function isDivider(line) {
    return line.trim() === '* * *';
}

/**
 * 제목 헤더(#) 보호
 */
function isHeader(line) {
    return line.trim().startsWith('#');
}

/**
 * 의성어/효과음 라인 보호
 * 예: "콰앙—! 쿠웅—! 쾅—!", "삐이이이—!", "지직—!"
 */
function isSoundEffect(line) {
    const trimmed = line.trim();
    if (trimmed.length > SOUND_EFFECT_MAX_LEN) return false;
    // 대시류(—, –, -)와 !/?가 포함된 짧은 줄은 효과음으로 판정
    return /[—\-–][!?]/.test(trimmed) || /^[ㄱ-ㅎ가-힣—\-–!?*\s]+$/.test(trimmed) && trimmed.length < SOUND_EFFECT_MAX_LEN;
}

/**
 * 대화문(따옴표) 라인 보호
 * 문단 내부에 큰따옴표(")나 따옴표 기호가 포함되어 있다면, 대사 흐름 및 따옴표 정합성 수호를 위해 통째로 보호
 */
function isDialogue(line) {
    const trimmed = line.trim();
    return /["「」『』“”]/.test(trimmed);
}

/**
 * 사법 기술 마킹 블록 보호 [ ... ]
 */
function isSystemMessage(line) {
    const trimmed = line.trim();
    return trimmed.startsWith('[') && trimmed.endsWith(']');
}

/**
 * 이탤릭 사고/회상 블록 보호 * ... *
 */
function isItalicBlock(line) {
    const trimmed = line.trim();
    return trimmed.startsWith('*') && trimmed.endsWith('*');
}

// ─────────────────────────────────────────────
// 🔧  핵심 가공 로직
// ─────────────────────────────────────────────

function processParagraph(para) {
    const trimmed = para.trim();

    // 빈 줄 → 그대로 통과
    if (trimmed === '') return para;

    // 보호 대상 블록: 그대로 통과
    if (isDivider(trimmed)) return '* * *';
    if (isHeader(trimmed)) return trimmed;
    if (isSoundEffect(trimmed)) return trimmed;
    if (isDialogue(trimmed)) return trimmed;
    if (isSystemMessage(trimmed)) return trimmed;
    if (isItalicBlock(trimmed)) return trimmed;

    // ── 문장 단위로 분리 (한국어 서술 종결어미 기준) ──
    // 마침표, 느낌표, 물음표 + 뒤에 공백 또는 줄끝
    const rawSentences = trimmed.split(/(?<=[.!?。])\s+/);

    let result = '';
    let currentChunkLen = 0;

    rawSentences.forEach((sentence, idx) => {
        const sLen = sentence.length;
        const isLast = idx === rawSentences.length - 1;

        result += sentence;
        currentChunkLen += sLen;

        if (!isLast) {
            // 누적 글자 수가 임계치 초과 시 문단 분리
            if (currentChunkLen >= MOBILE_PARA_THRESHOLD) {
                result += '\n\n';
                currentChunkLen = 0;
            } else {
                result += ' ';
            }
        }
    });

    return result.trim();
}

function applyReadability(filePath) {
    if (!fs.existsSync(filePath)) {
        console.error(`[오류] 파일을 찾을 수 없습니다: ${filePath}`);
        return false;
    }

    let text;
    try {
        text = fs.readFileSync(filePath, 'utf-8');
    } catch (e) {
        console.error(`[오류] 파일 읽기 실패: ${e.message}`);
        return false;
    }

    // 프론트매터(YAML) 보존
    const frontmatterMatch = text.match(/^---[\s\S]*?---\n/);
    const frontmatter = frontmatterMatch ? frontmatterMatch[0] : '';
    const body = text.replace(/^---[\s\S]*?---\n/, '');

    // 문단 단위로 분리 후 가공
    const paragraphs = body.split(/\n\s*\n/);
    const processed = paragraphs.map(processParagraph);

    const newText = frontmatter + processed.join('\n\n') + '\n';

    try {
        fs.writeFileSync(filePath, newText, 'utf-8');
        console.log(`[완료] 모바일 가독성 가공: ${path.basename(filePath)}`);
        return true;
    } catch (e) {
        console.error(`[오류] 파일 저장 실패: ${e.message}`);
        return false;
    }
}

// ─────────────────────────────────────────────
// 🚀  진입점 (단일 파일 / 배치 모드)
// ─────────────────────────────────────────────

const args = process.argv.slice(2);

if (args.length === 0) {
    console.log('Usage:');
    console.log('  단일 파일: node apply_readability.js <filepath.md>');
    console.log('  배치 모드: node apply_readability.js --batch <folder_path>');
    process.exit(1);
}

if (args[0] === '--batch') {
    // ── 배치 모드: 폴더 내 모든 .md 파일 처리 ──
    const folderPath = args[1];
    if (!folderPath || !fs.existsSync(folderPath)) {
        console.error('[오류] 유효한 폴더 경로를 지정하세요.');
        process.exit(1);
    }

    const files = fs.readdirSync(folderPath)
        .filter(f => f.endsWith('.md'))
        .sort();

    if (files.length === 0) {
        console.log('[알림] 처리할 .md 파일이 없습니다.');
        process.exit(0);
    }

    console.log(`\n🛡️  [apply_readability.js v2.0] 배치 모드 가동`);
    console.log(`📂  대상 폴더: ${folderPath}`);
    console.log(`📄  처리 대상: ${files.length}개 파일\n`);

    let successCount = 0;
    files.forEach(f => {
        const full = path.join(folderPath, f);
        if (applyReadability(full)) successCount++;
    });

    console.log(`\n✅  완료: ${successCount}/${files.length}개 파일 모바일 가독성 가공 완료`);

} else {
    // ── 단일 파일 모드 ──
    const filePath = args[0];
    applyReadability(filePath);
}

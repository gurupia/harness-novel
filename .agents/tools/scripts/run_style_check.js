const fs = require('fs');
const path = require('path');

function checkStyle(filePath) {
    if (!fs.existsSync(filePath)) {
        console.error(`Error: File not found: ${filePath}`);
        process.exit(1);
    }

    let text;
    try {
        text = fs.readFileSync(filePath, 'utf-8');
    } catch (e) {
        console.error(`Error reading file: ${e.message}`);
        process.exit(1);
    }

    // 1. Remove YAML frontmatter
    let textBody = text.replace(/^---[\s\S]*?---\n/, '');
    // 2. Remove titles/headers (lines starting with #)
    textBody = textBody.replace(/^#.*$/gm, '');
    
    // PASS 0: Length
    const charCount = textBody.trim().length;
    
    const pass0Status = charCount >= 5500 ? "🟢" : "🔴";
    let pass0Info = `${charCount}자`;
    if (charCount < 5500) {
        pass0Info += " (미달)";
    }

    // Early Exit if PASS 0 fails
    if (pass0Status === "🔴") {
        let earlyReport = `## 검증 리포트 자동 산출 (${path.basename(filePath)})\n\n`;
        earlyReport += "| PASS | 판정 | 비고 |\n";
        earlyReport += "|------|------|------|\n";
        earlyReport += `| 0 분량 | 🔴 | ${pass0Info} |\n\n`;
        earlyReport += "**종합 판정: 🔴 REWRITE (분량 미달로 인한 조기 종료)**\n";
        console.log(earlyReport);
        saveReport(filePath, earlyReport);
        return;
    }

    // PASS 1: Stutter Spam
    const words = textBody.split(/\s+/).filter(w => w.trim() !== "");
    const stutterSpams = [];
    for (let i = 0; i < words.length - 1; i++) {
        const w1 = words[i].replace(/[^\w가-힣]/g, '');
        const w2 = words[i + 1].replace(/[^\w가-힣]/g, '');
        if (w1 && w1 === w2 && w1.length > 0) {
            stutterSpams.push(`${words[i]} ${words[i + 1]}`);
        }
    }
    
    const pass1Critical = stutterSpams.length;
    const pass1Status = pass1Critical === 0 ? "🟢" : "🔴";
    const pass1Info = pass1Critical > 0 ? `발견됨: ${stutterSpams.slice(0, 3).join(', ')}` : "양호";

    // PASS 2: Meta Narrative & Quantitative Word Spam
    const metaPatterns = [
        /제\s*[0-9]+\s*(화|장|부)/g,
        /회차\s*[0-9]+/g,
        /피날레를 장식/g,
        /연재 마감/g
    ];
    let metaFindings = [];
    metaPatterns.forEach(pattern => {
        const matches = textBody.match(pattern);
        if (matches) {
            metaFindings = metaFindings.concat(matches);
        }
    });
    
    const metaCritical = metaFindings.length;
    
    // WS-03: System message overflow (> 80 chars)
    const systemMsgRegex = /[\[\(]([^\]\)]+)[\]\)]/g;
    let systemMsgWarnings = 0;
    let match;
    while ((match = systemMsgRegex.exec(textBody)) !== null) {
        if (match[1].length > 80) {
            systemMsgWarnings++;
        }
    }

    // WS-10: Paragraph length (> 120 chars)
    const paragraphs = textBody.split(/\n+/);
    let paraLengthWarnings = 0;
    paragraphs.forEach(p => {
        if (p.trim().length > 120) {
            paraLengthWarnings++;
        }
    });

    // WS-16: Pronoun Overuse Check
    const sentences = textBody.split(/[.!?]\s+/);
    let pronounWarnings = 0;
    const pronounFindings = [];
    const pronounRegex = /(?:^|\s)(그|그녀|그들)(?:이|가|은|는|의|를|을|에게|와|과|도|!|\?|,|\.|\s|$)/g;
    for (let i = 0; i < sentences.length - 2; i++) {
        const windowText = sentences.slice(i, i + 3).join(' ');
        const matches = windowText.match(pronounRegex);
        if (matches && matches.length >= 3) {
            pronounWarnings++;
            pronounFindings.push(windowText.trim());
        }
    }
    
    const warningSum = systemMsgWarnings + paraLengthWarnings + pronounWarnings;
    const pass2Status = metaCritical > 0 ? "🔴" : (warningSum > 0 ? "🟡" : "🟢");
    
    let pass2Info = "양호";
    if (metaCritical > 0) {
        pass2Info = `메타 서술 ${metaCritical}건 발견`;
    } else if (warningSum > 0) {
        pass2Info = `정량 오류 발견 (WS-03:${systemMsgWarnings}, WS-10:${paraLengthWarnings}, WS-16:${pronounWarnings})`;
    }

    // Generate Report Content
    let reportContent = `## 검증 리포트 자동 산출 (${path.basename(filePath)})\n\n`;
    reportContent += "| PASS | 판정 | 🔴 Critical | 🟡 Warning | 🔵 Info | 비고 |\n";
    reportContent += "|------|------|------------|-----------|--------|------|\n";
    reportContent += `| 0 분량 | ${pass0Status} | — | — | — | ${pass0Info} |\n`;
    reportContent += `| 1 문법 | ${pass1Status} | ${pass1Critical}건 | 0건 | 0건 | ${pass1Info} |\n`;
    reportContent += `| 2 문체 | ${pass2Status} | ${metaCritical}건 | ${warningSum}건 | 0건 | ${pass2Info} |\n`;
    reportContent += `| 3 설정 | ⚪ | - | - | - | 수동 검증 요망 |\n`;
    reportContent += `| 4 서사 | ⚪ | - | - | - | 수동 검증 요망 |\n\n`;
    
    if (pass1Status === "🔴" || pass2Status === "🔴") {
        reportContent += "**종합 판정: 🔴 REWRITE 필요 (스크립트 판정)**\n";
    } else if (pass2Status === "🟡") {
        reportContent += "**종합 판정: 🟡 REVISE 필요 (정량적 수치 조정 권장)**\n";
    } else {
        reportContent += "**종합 판정: 🟢 정량적 조건 PASS (정성 평가 진행 요망)**\n";
    }

    if (pronounFindings.length > 0) {
        reportContent += "\n### 🟡 대명사 남용 의심 구간\n";
        pronounFindings.slice(0, 5).forEach((f, idx) => {
            reportContent += `${idx + 1}. "...${f}..."\n`;
        });
    }

    // Output to console
    console.log(reportContent);
    saveReport(filePath, reportContent);
}

function saveReport(filePath, reportContent) {
    try {
        const fileBasename = path.basename(filePath, '.md');
        const projectRoot = path.resolve(filePath, '..', '..', '..');
        const qaDir = path.join(projectRoot, 'qa', 'style_checks');

        if (!fs.existsSync(qaDir)) {
            fs.mkdirSync(qaDir, { recursive: true });
        }

        const reportPath = path.join(qaDir, `${fileBasename}_Report.md`);
        fs.writeFileSync(reportPath, reportContent, 'utf-8');
        console.log(`리포트가 파일로 저장되었습니다: ${reportPath}`);
    } catch (e) {
        console.error(`Error saving report file: ${e.message}`);
    }
}

if (process.argv.length < 3) {
    console.log("Usage: node run_style_check.js <filepath>");
    process.exit(1);
}

const filePath = process.argv[2];
checkStyle(filePath);

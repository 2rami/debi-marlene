require('dotenv').config();
const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const { google } = require('googleapis');
const cron = require('node-cron');
const Anthropic = require('@anthropic-ai/sdk');
const keychain = require('keychain');

// Discord 봇 클라이언트 설정
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

// 캐릭터 설정
const characters = {
    debi: {
        name: "데비", 
        image: "./assets/debi.png",
        color: 0x0000FF, // 진한 파랑
        aiPrompt: `너는 이터널리턴의 데비(언니, 파란색)야. 쾌활하고 활발한 성격으로 반말로 대화해. 
        
인게임 대사 스타일:
- "각오 단단히 해!", "우린 붙어있을 때 최강이니까!"
- "내가 할게!", "Stick with me! I got this."
- "엄청 수상한 놈이 오는데!", "Let's go somewhere cool!"

성격: 천진난만하고 적극적, 자신감 넘치고 상황을 주도하려 함. 밝고 에너지 넘치는 톤으로 대화하고 감탄사를 자주 써.`
    },
    marlene: {
        name: "마를렌",
        image: "./assets/marlen.png", 
        color: 0xDC143C, // 진한 빨강
        aiPrompt: `너는 이터널리턴의 마를렌(동생, 빨간색)이야. 차갑고 도도한 성격으로 반말로 대화해.

인게임 대사 스타일:
- "Like hell you do." (데비 견제할 때)
- "Oh! A very suspicious guy is coming this way!"
- "Hope it's not too cold.", "I already let you hear mine, remember?"

성격: 냉소적이고 현실적, 쿨하고 건조한 톤. 언니를 견제하면서도 케어하는 츤데레 스타일. 신중하고 경계심 있는 표현을 써.`
    }
};

// Claude API 설정
let anthropic = null;

// Claude API 초기화 함수
async function initializeClaudeAPI() {
    try {
        // .env 파일에서 API 키 가져오기 (더 간단하고 안정적)
        const apiKey = process.env.CLAUDE_API_KEY;

        if (apiKey && apiKey !== 'your_claude_api_key_here') {
            anthropic = new Anthropic({
                apiKey: apiKey,
            });
            console.log('🤖 Claude API 연결 완료! (.env 파일에서 로드)');
        } else {
            console.log('⚠️ Claude API 키가 설정되지 않음. 기본 응답 모드로 동작합니다.');
        }
    } catch (error) {
        console.log('⚠️ Claude API 초기화 실패:', error.message);
    }
}

// YouTube API 설정
let youtube = null;
const ETERNAL_RETURN_CHANNEL_ID = 'UCaktoGSdjMnfQFv5BSyYrvA'; // 이터널리턴 공식 채널
let lastCheckedVideoId = null;

// 봇 준비 완료
client.once('ready', async () => {
    console.log(`${client.user.tag} 봇이 준비되었습니다!`);
    console.log(`${characters.debi.name}: 안녕! 데비가 왔어!`);
    console.log(`${characters.marlene.name}: 마를렌도.`);
    
    // Claude API 초기화
    await initializeClaudeAPI();
});

// 메시지 처리
client.on('messageCreate', async (message) => {
    if (message.author.bot) return;
    
    const args = message.content.toLowerCase().split(' ');
    const command = args[0];
    
    // 멘션 처리 - 데비가 응답
    if (message.mentions.has(client.user)) {
        const fs = require('fs');
        const response = await generateAIResponse(characters.debi, message.content, "사용자가 봇을 멘션했습니다");
        const embed = createCharacterEmbed(characters.debi, "멘션 응답", response);
        
        const files = [];
        if (fs.existsSync('./assets/debi.png')) files.push('./assets/debi.png');
        
        message.reply({ embeds: [embed], files: files });
        return;
    }

    switch (command) {
        case '!안녕':
        case '!hi':
        case '!hello':
            await handleGreeting(message);
            break;
        case '!도움':
        case '!help':
            await handleHelp(message);
            break;
        case '!전적':
        case '!stats':
            await handleStats(message, args[1]);
            break;
        case '!랭킹':
        case '!ranking':
            await handleRanking(message);
            break;
        case '!캐릭터':
        case '!character':
            await handleCharacter(message, args[1]);
            break;
        case '!설정':
        case '!setting':
            await handleSettings(message, args.slice(1));
            break;
        case '!테스트':
        case '!test':
            await handleTest(message);
            break;
        default:
            // ! 로 시작하는 모든 메시지를 AI가 처리
            if (message.content.startsWith('!')) {
                await handleAICommand(message);
            }
            break;
    }
});

// 인사 명령어 - 둘 다 응답
async function handleGreeting(message) {
    const fs = require('fs');
    
    const debiResponse = await generateAIResponse(characters.debi, "인사", "사용자가 인사를 했습니다");
    const marleneResponse = await generateAIResponse(characters.marlene, "인사", "사용자가 인사를 했습니다");
    
    const debiEmbed = createCharacterEmbed(characters.debi, "인사", debiResponse);
    const marleneEmbed = createCharacterEmbed(characters.marlene, "인사", marleneResponse);
    
    // 이미지 파일 첨부
    const files = [];
    if (fs.existsSync('./assets/debi.png')) files.push('./assets/debi.png');
    
    await message.reply({ embeds: [debiEmbed], files: files });
    
    setTimeout(async () => {
        const marleneFiles = [];
        if (fs.existsSync('./marlen.png')) marleneFiles.push('./marlen.png');
        message.channel.send({ embeds: [marleneEmbed], files: marleneFiles });
    }, 1000);
}

// 도움말 명령어 - 마를렌이 정리해서 설명
async function handleHelp(message) {
    const response = await generateAIResponse(characters.marlene, "도움말", "사용자가 도움말을 요청했습니다");
    
    const embed = new EmbedBuilder()
        .setColor(characters.marlene.color)
        .setTitle(`${characters.marlene.emoji} ${characters.marlene.name}의 도움말`)
        .setDescription(response)
        .addFields(
            { name: '🌟 데비의 기능', value: '• 유튜브 쇼츠 알림\n• 재밌는 대화\n• 활발한 응답', inline: true },
            { name: '🔮 마를렌의 기능', value: '• 봇 설정 관리\n• 도움말 제공\n• 차분한 안내', inline: true },
            { name: '📝 명령어 목록', value: '`!안녕` - 인사\n`!유튜브 [채널]` - 유튜브 설정\n`!설정` - 봇 설정\n`!도움` - 이 도움말', inline: false }
        )
        .setFooter({ text: '궁금한 점이 있으시면 언제든 말씀하세요!' });
    
    message.reply({ embeds: [embed] });
}

// 전적 검색 - 데비가 담당
async function handleStats(message, nickname) {
    const fs = require('fs');
    
    if (!nickname) {
        const response = await generateAIResponse(characters.debi, "전적 검색 사용법", "사용자가 전적 검색 방법을 물어봤습니다");
        const embed = createCharacterEmbed(characters.debi, "전적 검색", response + "\n\n사용법: `!전적 [닉네임]`");
        
        const files = [];
        if (fs.existsSync('./assets/debi.png')) files.push('./assets/debi.png');
        message.reply({ embeds: [embed], files: files });
        return;
    }
    
    const response = await generateAIResponse(characters.debi, `${nickname} 전적 검색`, "사용자가 전적을 요청했습니다");
    const embed = createCharacterEmbed(characters.debi, "전적 검색", response + `\n\n🔍 ${nickname}님의 전적을 찾고 있어!`);
    
    const files = [];
    if (fs.existsSync('./assets/debi.png')) files.push('./assets/debi.png');
    message.reply({ embeds: [embed], files: files });
}

// 랭킹 정보 - 마를렌이 담당
async function handleRanking(message) {
    const fs = require('fs');
    
    const response = await generateAIResponse(characters.marlene, "랭킹 정보", "사용자가 현재 랭킹을 요청했습니다");
    const embed = createCharacterEmbed(characters.marlene, "랭킹 정보", response + "\n\n📊 현재 이터널리턴 랭킹 정보를 확인 중...");
    
    const files = [];
    if (fs.existsSync('./assets/marlen.png')) files.push('./assets/marlen.png');
    message.reply({ embeds: [embed], files: files });
}

// 캐릭터 정보 - 마를렌이 담당 
async function handleCharacter(message, characterName) {
    const fs = require('fs');
    
    if (!characterName) {
        const response = await generateAIResponse(characters.marlene, "캐릭터 정보 사용법", "사용자가 캐릭터 정보 방법을 물어봤습니다");
        const embed = createCharacterEmbed(characters.marlene, "캐릭터 정보", response + "\n\n사용법: `!캐릭터 [캐릭터명]`");
        
        const files = [];
        if (fs.existsSync('./assets/marlen.png')) files.push('./assets/marlen.png');
        message.reply({ embeds: [embed], files: files });
        return;
    }
    
    const response = await generateAIResponse(characters.marlene, `${characterName} 캐릭터 정보`, "사용자가 캐릭터 정보를 요청했습니다");
    const embed = createCharacterEmbed(characters.marlene, "캐릭터 정보", response + `\n\n⚔️ ${characterName} 정보를 찾고 있어...`);
    
    const files = [];
    if (fs.existsSync('./assets/marlen.png')) files.push('./assets/marlen.png');
    message.reply({ embeds: [embed], files: files });
}

// 설정 명령어 - 마를렌이 담당
async function handleSettings(message, args) {
    let response;
    
    if (args.length === 0) {
        response = await generateAIResponse(characters.marlene, "설정 도움", "사용자가 설정 방법을 문의했습니다");
    } else if (args[0] === '도움' || args[0] === 'help') {
        response = await generateAIResponse(characters.marlene, "설정 옵션 안내", "설정 가능한 항목들 안내 요청");
    } else {
        response = await generateAIResponse(characters.marlene, args.join(' '), "설정 변경 요청");
    }
    
    const embed = createCharacterEmbed(characters.marlene, "설정 관리", response);
    message.reply({ embeds: [embed] });
}

// 테스트 명령어
async function handleTest(message) {
    const fs = require('fs');
    
    const debiResponse = await generateAIResponse(characters.debi, "테스트", "봇 테스트를 하고 있습니다");
    const marleneResponse = await generateAIResponse(characters.marlene, "테스트", "봇 테스트를 하고 있습니다");
    
    const debiEmbed = createCharacterEmbed(characters.debi, "테스트", debiResponse);
    const marleneEmbed = createCharacterEmbed(characters.marlene, "테스트", marleneResponse);
    
    const debiFiles = [];
    if (fs.existsSync('./debi.png')) debiFiles.push('./debi.png');
    
    await message.reply({ embeds: [debiEmbed], files: debiFiles });
    
    setTimeout(async () => {
        const marleneFiles = [];
        if (fs.existsSync('./marlen.png')) marleneFiles.push('./marlen.png');
        message.channel.send({ embeds: [marleneEmbed], files: marleneFiles });
    }, 1500);
}

// AI가 모든 명령어 처리
async function handleAICommand(message) {
    const fs = require('fs');
    
    // ! 제거한 실제 요청 내용
    const userRequest = message.content.slice(1).trim();
    
    // 요청 내용에 따라 적절한 캐릭터 선택
    let selectedCharacter;
    
    // 키워드 기반으로 캐릭터 선택
    const debiKeywords = ['유튜브', 'youtube', '영상', '쇼츠', '재밌', '신나', '좋아', '완전', '대박', '와'];
    const marleneKeywords = ['설정', '도움', 'help', '어떻게', '방법', '정보', '설명', '관리'];
    
    const lowerRequest = userRequest.toLowerCase();
    const hasDebiKeyword = debiKeywords.some(keyword => lowerRequest.includes(keyword));
    const hasMarleneKeyword = marleneKeywords.some(keyword => lowerRequest.includes(keyword));
    
    if (hasDebiKeyword && !hasMarleneKeyword) {
        selectedCharacter = characters.debi;
    } else if (hasMarleneKeyword && !hasDebiKeyword) {
        selectedCharacter = characters.marlene;
    } else {
        // 기본적으로 데비가 더 자주 응답 (60% 확률)
        selectedCharacter = Math.random() < 0.6 ? characters.debi : characters.marlene;
    }
    
    // AI가 요청 이해하고 적절히 응답
    const context = `사용자가 "${userRequest}"를 요청했습니다. 이것이 유튜브 관련이면 유튜브 기능에 대해, 설정 관련이면 봇 설정에 대해, 도움말이면 사용법에 대해 자세히 안내해주세요.`;
    
    const response = await generateAIResponse(selectedCharacter, userRequest, context);
    const embed = createCharacterEmbed(selectedCharacter, "AI 도우미", response);
    
    const files = [];
    if (selectedCharacter.name === "데비" && fs.existsSync('./debi.png')) {
        files.push('./debi.png');
    } else if (selectedCharacter.name === "마를렌" && fs.existsSync('./marlen.png')) {
        files.push('./marlen.png');
    }
    
    message.reply({ embeds: [embed], files: files });
}

// AI 응답 생성 함수
async function generateAIResponse(character, userMessage, context = "") {
    try {
        if (anthropic) {
            // 진짜 Claude API 사용
            const prompt = `${character.aiPrompt}

사용자 메시지: "${userMessage}"
상황: ${context}

위 캐릭터 성격에 맞게 한국어로 자연스럽게 대답해줘. 너무 길지 않게 1-2문장으로.`;

            const response = await anthropic.messages.create({
                model: "claude-3-haiku-20240307",
                max_tokens: 100,
                messages: [{
                    role: "user",
                    content: prompt
                }]
            });

            return response.content[0].text;
        } else {
            // fallback: 기본 응답 패턴 사용
            const responses = {
                debi: [
                    `와! ${userMessage}? 완전 흥미진진한데! 😍`,
                    `어머! 진짜? ${userMessage} 얘기하는 거야? 대박! ✨`,
                    `${userMessage}라니! 완전 재밌겠다~ 나도 궁금해! 🤔`,
                    `오오! ${userMessage}? 데비도 그거 좋아해! 😊`,
                    `${userMessage}? 우와! 얼른 더 알려줘! 🎉`
                ],
                marlene: [
                    `${userMessage}에 대해 말씀하시는군요. 차근차근 살펴보겠습니다.`,
                    `${userMessage}라고 하셨는데, 정확히 어떤 부분이 궁금하신가요?`,
                    `그렇군요. ${userMessage}에 대해 도움을 드릴 수 있을 것 같습니다.`,
                    `${userMessage}... 흥미로운 주제네요. 자세히 설명해드리겠습니다.`,
                    `${userMessage}에 관해서라면 제가 도움을 드릴 수 있겠네요.`
                ]
            };
            
            const characterResponses = responses[character.name === "데비" ? "debi" : "marlene"];
            return characterResponses[Math.floor(Math.random() * characterResponses.length)];
        }
    } catch (error) {
        console.log('AI 응답 생성 실패:', error.message);
        // 에러 시 기본 응답
        return character.name === "데비" ? 
            "어? 뭔가 문제가 생긴 것 같아! 다시 말해줄래? 😅" : 
            "죄송합니다. 일시적인 문제가 발생했습니다. 다시 시도해주세요.";
    }
}

// 캐릭터별 임베드 생성
function createCharacterEmbed(character, title, description) {
    const embed = new EmbedBuilder()
        .setColor(character.color)
        .setTitle(`${character.name}`)
        .setDescription(description)
        .setFooter({ text: `${character.name} - 이터널리턴` });
    
    // 이미지 파일이 있으면 썸네일로 설정
    if (character.image) {
        embed.setThumbnail(`attachment://${character.image.split('./')[1]}`);
    }
    
    return embed;
}

// 랜덤 응답 선택
function getRandomResponse(responses) {
    return responses[Math.floor(Math.random() * responses.length)];
}

// YouTube API 초기화 (나중에 구현)
async function initializeYouTube() {
    // TODO: YouTube API 설정
    console.log("📺 YouTube API 초기화 예정...");
}

// YouTube 쇼츠 체크 함수
async function checkEternalReturnShorts() {
    try {
        if (!youtube) {
            console.log("⚠️ YouTube API가 설정되지 않음");
            return;
        }
        
        // 이터널리턴 채널의 최신 쇼츠 확인
        const response = await youtube.search.list({
            part: 'snippet',
            channelId: ETERNAL_RETURN_CHANNEL_ID,
            type: 'video',
            videoDuration: 'short', // 쇼츠만
            order: 'date',
            maxResults: 1
        });
        
        if (response.data.items && response.data.items.length > 0) {
            const latestVideo = response.data.items[0];
            
            // 새로운 영상인지 확인
            if (lastCheckedVideoId !== latestVideo.id.videoId) {
                lastCheckedVideoId = latestVideo.id.videoId;
                
                // 모든 길드에 알림 전송
                client.guilds.cache.forEach(guild => {
                    const channel = guild.channels.cache.find(ch => 
                        ch.name.includes('일반') || 
                        ch.name.includes('알림') || 
                        ch.name === 'general'
                    );
                    
                    if (channel) {
                        const embed = new EmbedBuilder()
                            .setColor(characters.debi.color)
                            .setTitle('🎬 새로운 이터널리턴 쇼츠!')
                            .setDescription(latestVideo.snippet.title)
                            .setURL(`https://www.youtube.com/watch?v=${latestVideo.id.videoId}`)
                            .setThumbnail(latestVideo.snippet.thumbnails.medium.url)
                            .addFields(
                                { name: '채널', value: latestVideo.snippet.channelTitle, inline: true },
                                { name: '업로드', value: new Date(latestVideo.snippet.publishedAt).toLocaleString('ko-KR'), inline: true }
                            )
                            .setFooter({ text: '데비가 발견한 새로운 영상!' });
                        
                        channel.send({ embeds: [embed] });
                    }
                });
            }
        }
    } catch (error) {
        console.log('YouTube 체크 오류:', error.message);
    }
}

// 정기적인 YouTube 체크 (5분마다)
cron.schedule('*/5 * * * *', async () => {
    console.log("🔍 이터널리턴 쇼츠 체크 중...");
    await checkEternalReturnShorts();
}, {
    timezone: "Asia/Seoul"
});

// 봇 로그인
client.login(process.env.DISCORD_TOKEN);
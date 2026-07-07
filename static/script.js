let emails = [];
let currentEmail = null;

// DOM Elements
const emailListEl = document.getElementById('email-list');
const incomingSection = document.getElementById('incoming-section');
const incomingEmailBody = document.getElementById('incoming-email-body');
const currentCategory = document.getElementById('current-category');
const actionBar = document.getElementById('action-bar');
const btnGenerate = document.getElementById('btn-generate');
const generateLoader = document.getElementById('generate-loader');
const replySection = document.getElementById('reply-section');
const generatedReplyBody = document.getElementById('generated-reply-body');
const btnEvaluate = document.getElementById('btn-evaluate');
const evaluateLoader = document.getElementById('evaluate-loader');
const scorecard = document.getElementById('scorecard');

// Fetch emails on load
async function fetchEmails() {
    try {
        const res = await fetch('/api/emails');
        const data = await res.json();
        emails = data.emails;
        renderEmailList();
    } catch (err) {
        console.error("Failed to load emails", err);
    }
}

function renderEmailList() {
    emailListEl.innerHTML = '';
    emails.forEach(email => {
        const div = document.createElement('div');
        div.className = 'email-item';
        div.innerHTML = `
            <div class="email-category">${email.category.replace('_', ' ')}</div>
            <div class="email-preview">${email.incoming_email}</div>
        `;
        div.onclick = () => selectEmail(email, div);
        emailListEl.appendChild(div);
    });
}

function selectEmail(email, element) {
    // Update active class
    document.querySelectorAll('.email-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');

    currentEmail = email;
    currentCategory.innerText = `Category: ${email.category.replace('_', ' ')}`;
    
    // Reset UI state
    incomingSection.style.display = 'block';
    incomingEmailBody.innerText = email.incoming_email;
    actionBar.style.display = 'flex';
    replySection.style.display = 'none';
    scorecard.style.display = 'none';
    btnGenerate.disabled = false;
    btnEvaluate.disabled = false;
    generatedReplyBody.value = '';
}

// Generate Reply
btnGenerate.onclick = async () => {
    if (!currentEmail) return;
    
    btnGenerate.disabled = true;
    generateLoader.style.display = 'block';
    
    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ incoming_email: currentEmail.incoming_email })
        });
        const data = await res.json();
        
        generatedReplyBody.value = data.reply;
        replySection.style.display = 'block';
        
    } catch (err) {
        alert("Failed to generate reply");
    } finally {
        btnGenerate.disabled = false;
        generateLoader.style.display = 'none';
    }
};

// Evaluate Reply
btnEvaluate.onclick = async () => {
    const replyText = generatedReplyBody.value;
    if (!currentEmail || !replyText) return;
    
    btnEvaluate.disabled = true;
    evaluateLoader.style.display = 'block';
    scorecard.style.display = 'none';
    
    try {
        const res = await fetch('/api/evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                incoming_email: currentEmail.incoming_email,
                generated_reply: replyText
            })
        });
        const data = await res.json();
        
        // Populate Scorecard
        document.getElementById('score-relevance').innerText = `${data.relevance_score}/5`;
        document.getElementById('bar-relevance').style.width = `${(data.relevance_score / 5) * 100}%`;
        
        document.getElementById('score-tone').innerText = `${data.tone_score}/5`;
        document.getElementById('bar-tone').style.width = `${(data.tone_score / 5) * 100}%`;
        
        document.getElementById('score-accuracy').innerText = `${data.accuracy_score}/5`;
        document.getElementById('bar-accuracy').style.width = `${(data.accuracy_score / 5) * 100}%`;
        
        document.getElementById('eval-reasoning').innerText = data.reasoning;
        
        scorecard.style.display = 'block';
        
    } catch (err) {
        alert("Failed to evaluate reply");
    } finally {
        btnEvaluate.disabled = false;
        evaluateLoader.style.display = 'none';
    }
};

// Initialize
fetchEmails();

/**
 * MediGuard API Client
 * Handles all communication between frontend and backend
 */

const API_BASE = (window.MEDIGUARD_API_BASE || '').replace(/\/$/, '');

/**
 * Assess medication safety
 */
async function assessMedication(drug1, drug2, condition) {
    console.log(`Assessing: ${drug1} + ${drug2} for condition: ${condition}`);
    
    try {
        const response = await fetch(`${API_BASE}/assess`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            credentials: "include",   // ✅ send session cookie
            body: JSON.stringify({
                drug1: drug1.trim(),
                drug2: drug2.trim(),
                condition: condition.trim()
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.status === "success") {
            return { success: true, data: result.data };
        } else {
            return { success: false, error: result.message || "Assessment failed" };
        }
    } catch (error) {
        console.error("API Error:", error);
        return { success: false, error: error.message };
    }
}

/**
 * Get risk level severity
 */
function getRiskSeverity(riskLevel) {
    const riskMap = {
        "High":     { color: "#D32F2F", icon: "⚠️", label: "High Risk" },
        "Moderate": { color: "#F57C00", icon: "⚡", label: "Moderate Risk" },
        "Low":      { color: "#FBC02D", icon: "ℹ️", label: "Low Risk" },
        "None":     { color: "#388E3C", icon: "✓",  label: "Safe" }
    };
    return riskMap[riskLevel] || { color: "#757575", icon: "?", label: "Unknown" };
}

/**
 * Display assessment results
 */
function displayResults(result) {
    if (!result.success) {
        return `
            <div style="background:#FFEBEE;color:#C62828;padding:20px;border-radius:8px;border-left:4px solid #F44336;margin-top:20px;">
                ❌ Error: ${result.error || 'Assessment failed'}
            </div>`;
    }

    const data = result.data;
    const overallSeverity = getRiskSeverity(data.overall_risk);
    
    return `
    <div style="border-left:4px solid ${overallSeverity.color};padding:20px;background:#f5f5f5;border-radius:8px;margin-top:16px;">
        <h3 style="color:${overallSeverity.color};margin-top:0;">
            ${overallSeverity.icon} Overall: ${overallSeverity.label}
        </h3>
        <div style="margin-top:15px;">
            <p><strong>Drug-Drug Interaction:</strong> ${data.ddi_risk}</p>
            <p><strong>Drug-Food (${data.drug1 || 'Drug 1'}):</strong> ${data.dfi_risk_drug1}</p>
            <p><strong>Drug-Food (${data.drug2 || 'Drug 2'}):</strong> ${data.dfi_risk_drug2}</p>
            <p><strong>Drug-Condition (${data.drug1 || 'Drug 1'}):</strong> ${data.dci_risk_drug1}</p>
            <p><strong>Drug-Condition (${data.drug2 || 'Drug 2'}):</strong> ${data.dci_risk_drug2}</p>
        </div>
        <hr/>
        <h4>Recommendation:</h4>
        ${getRecommendation(data.overall_risk)}
    </div>`;
}

/**
 * Get recommendation based on risk level
 */
function getRecommendation(riskLevel) {
    const recommendations = {
        "High": `<div style="background:#FFEBEE;padding:10px;border-radius:5px;color:#C62828;">
            <strong>⚠️ HIGH RISK - Consult Healthcare Provider</strong><br/>
            This combination poses significant safety concerns. Do NOT take without consulting a doctor or pharmacist immediately.
        </div>`,
        "Moderate": `<div style="background:#FFF3E0;padding:10px;border-radius:5px;color:#E65100;">
            <strong>⚡ MODERATE RISK - Use with Caution</strong><br/>
            This combination requires medical supervision. Consult your healthcare provider before using.
        </div>`,
        "Low": `<div style="background:#FFFDE7;padding:10px;border-radius:5px;color:#F57F17;">
            <strong>ℹ️ LOW RISK - Proceed with Care</strong><br/>
            While generally safe, monitor for any side effects and follow dosage instructions carefully.
        </div>`,
        "None": `<div style="background:#E8F5E9;padding:10px;border-radius:5px;color:#2E7D32;">
            <strong>✓ SAFE</strong><br/>
            No known significant interactions detected. Follow your doctor's prescribed dosage.
        </div>`
    };
    return recommendations[riskLevel] || `<p>Unable to assess risk. Consult a healthcare professional.</p>`;
}

/**
 * Handle assessment form submit
 */
async function handleAssessment(event) {
    event.preventDefault();
    
    const drug1     = document.getElementById("drug1")?.value?.trim();
    const drug2     = document.getElementById("drug2")?.value?.trim();
    const condition = document.getElementById("condition")?.value?.trim();
    
    if (!drug1 || !drug2 || !condition) {
        alert("Please fill in all fields");
        return;
    }
    
    const resultsDiv = document.getElementById("results");
    if (resultsDiv) {
        resultsDiv.innerHTML = `<p style="text-align:center;color:#1565C0;font-weight:bold;">🔄 Analyzing medication interactions...</p>`;
    }
    
    // Call assessment API
    const result = await assessMedication(drug1, drug2, condition);
    
    if (resultsDiv) {
        resultsDiv.innerHTML = displayResults(result.success ? { success: true, data: result.data } : { success: false, error: result.error });
    }

    if (result.success) {
        // ✅ FIXED: Save using session cookies (no localStorage check needed)
        try {
            const saveResponse = await fetch(`${API_BASE}/api/assessments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',   // ✅ uses Flask session cookie
                body: JSON.stringify({
                    drug1,
                    drug2,
                    condition,
                    ddi_risk:      result.data.ddi_risk      || 'None',
                    dfi_risk_drug1: result.data.dfi_risk_drug1 || 'None',
                    dfi_risk_drug2: result.data.dfi_risk_drug2 || 'None',
                    dci_risk_drug1: result.data.dci_risk_drug1 || 'None',
                    dci_risk_drug2: result.data.dci_risk_drug2 || 'None',
                    overall_risk:  result.data.overall_risk  || 'None'
                })
            });

            if (saveResponse.ok) {
                console.log('✓ Assessment saved to history');
                // Refresh stats & history on dashboard if those functions exist
                if (typeof loadHistory === 'function') loadHistory();
            } else {
                console.warn('Assessment save returned:', saveResponse.status);
            }
        } catch (error) {
            console.warn('Could not save to history:', error);
        }
    }
}

/**
 * Handle logout
 */
async function handleLogout() {
    try {
        await fetch(`${API_BASE}/api/logout`, {
            method: 'POST',
            credentials: 'include'
        });
    } catch(e) {}
    window.location.href = '/login';
}
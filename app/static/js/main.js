document.getElementById('url-input').addEventListener('input', toggleFields)
document.getElementById('html-input').addEventListener('input', toggleFields)
document
	.getElementById('lint-form')
	.addEventListener('submit', handleFormSubmit)

function toggleFields() {
	const urlInput = document.getElementById('url-input')
	const htmlInput = document.getElementById('html-input')
	if (urlInput.value.trim()) htmlInput.disabled = true
	else htmlInput.disabled = false
	if (htmlInput.value.trim()) urlInput.disabled = true
	else urlInput.disabled = false
}

async function handleFormSubmit(e) {
	e.preventDefault()
	const reportDiv = document.getElementById('report')
	reportDiv.innerHTML =
		'<div class="spinner-border" role="status"><span class="visually-hidden">Loading…</span></div>'

	const url = document.getElementById('url-input').value.trim()
	const html = document.getElementById('html-input').value.trim()
	let endpoint, payload

	if (url) {
		endpoint = '/api/lint-url'
		payload = { url }
	} else if (html) {
		endpoint = '/api/lint-html'
		payload = { html }
	} else {
		reportDiv.innerHTML =
			'<div class="alert alert-warning">Enter URL or HTML.</div>'
		return
	}

	try {
		const resp = await fetch(endpoint, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload),
		})
		const data = await resp.json()
		if (!resp.ok) throw new Error(data.detail || 'Error')
		renderReport(data)
	} catch (err) {
		reportDiv.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`
	}
}

function renderReport(data) {
	const container = document.getElementById('report')

	const totalIssues = data.sections.reduce(
		(sum, sec) => sum + sec.issues.length,
		0
	)
	if (totalIssues === 0) {
		container.innerHTML =
			'<div class="alert alert-success">No issues found!</div>'
		return
	}

	let html = `
    <h4>Summary</h4>
    <ul>
      <li>Total: ${data.summary.total}</li>
      <li>Errors: ${data.summary.errors}</li>
      <li>Warnings: ${data.summary.warnings}</li>
    </ul>
    <div class="accordion" id="reportAccordion">
  `

	data.sections.forEach((section, idx) => {
		const headerId = `heading${idx}`
		const collapseId = `collapse${idx}`
		const issues = section.issues

		html += `
      <div class="accordion-item">
        <h2 class="accordion-header" id="${headerId}">
          <button class="accordion-button ${idx > 0 ? 'collapsed' : ''}" 
                  type="button" 
                  data-bs-toggle="collapse" 
                  data-bs-target="#${collapseId}" 
                  aria-expanded="${idx === 0}" 
                  aria-controls="${collapseId}">
            ${section.name} — ${issues.length} issues
          </button>
        </h2>
        <div id="${collapseId}" 
             class="accordion-collapse collapse ${idx === 0 ? 'show' : ''}" 
             aria-labelledby="${headerId}" 
             data-bs-parent="#reportAccordion">
          <div class="accordion-body">
    `

		if (issues.length === 0) {
			html += `<div class="text-success">No issues in this section</div>`
		} else {
			html += `
        <table class="table table-sm table-striped">
          <thead>
            <tr>
              <th>Code</th>
              <th>Message</th>
              <th>Selector</th>
              <th>Context</th>
            </tr>
          </thead>
          <tbody>
      `

			issues.forEach(issue => {
				const ctxFull = issue.context || '-'
				const snippet =
					ctxFull.length > 50
						? ctxFull.slice(0, 50).replace(/</g, '&lt;').replace(/>/g, '&gt;') +
						  '…'
						: ctxFull.replace(/</g, '&lt;').replace(/>/g, '&gt;')
				const tooltipAttr =
					ctxFull.length > 50
						? ` data-bs-toggle="tooltip" title="${ctxFull.replace(
								/"/g,
								'&quot;'
						  )}"`
						: ''

				html += `
          <tr>
            <td>${issue.code}</td>
            <td>${issue.message}</td>
            <td>${issue.selector || '-'}</td>
            <td><span${tooltipAttr}><code>${snippet}</code></span></td>
          </tr>
        `
			})

			html += `
          </tbody>
        </table>
      `
		}

		html += `
          </div>
        </div>
      </div>
    `
	})

	html += `</div>`
	container.innerHTML = html

	document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
		new bootstrap.Tooltip(el)
	})
}

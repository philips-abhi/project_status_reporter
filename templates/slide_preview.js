<!-- Slide Preview Template -->
<script>
function renderSlidePreview(data, containerId) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Container with id "${containerId}" not found`);
    return;
  }

  const slides = [
    {
      title: "Title Slide",
      content: `
        <div style="text-align: center; padding: 20px;">
          <h2 style="color: #7C3AED; margin-bottom: 10px;">${data.project_name}</h2>
          <p style="color: #ddd; margin: 5px 0;">${data.owner} • ${new Date().toISOString().split('T')[0]}</p>
          <p style="color: #ddd; margin: 10px 0;">Team: ${data.team_members.join(', ')}</p>
        </div>
      `
    },
    {
      title: "Results So Far",
      content: `
        <div style="padding: 15px;">
          <h3 style="color: #7C3AED; margin-bottom: 10px;">Results So Far</h3>
          <ul style="color: #eee; margin: 0; padding-left: 20px;">
            ${data.results_so_far.split('\n').filter(l => l.trim()).map(line => 
              `<li>${line.trim().replace(/^[-•]/, '').trim()}</li>`
            ).join('')}
          </ul>
        </div>
      `
    },
    {
      title: "Task Status",
      content: `
        <div style="padding: 15px;">
          <h3 style="color: #7C3AED; margin-bottom: 10px;">Task Status</h3>
          <table style="width: 100%; color: #eee; font-size: 12px; border-collapse: collapse;">
            <tr style="background: #7C3AED; color: #1E1E2E;">
              <th style="padding: 5px; text-align: left;">Task</th>
              <th style="padding: 5px; text-align: left;">Resp.</th>
              <th style="padding: 5px; text-align: left;">Status</th>
            </tr>
            ${data.tasks.slice(0, 3).map(task => {
              const statusColors = {
                'done': '#10B981',
                'in_progress': '#F59E0B',
                'not_started': '#EF4444'
              };
              return `<tr style="background: ${statusColors[task.status] || '#EF4444'}33;">
                <td style="padding: 5px; max-width: 100px; overflow: hidden; text-overflow: ellipsis;">${task.description.substring(0, 20)}</td>
                <td style="padding: 5px;">${task.responsible}</td>
                <td style="padding: 5px;">${task.status.replace('_', ' ').toUpperCase()}</td>
              </tr>`;
            }).join('')}
          </table>
        </div>
      `
    },
    {
      title: "Next Steps",
      content: `
        <div style="padding: 15px;">
          <h3 style="color: #7C3AED; margin-bottom: 10px;">Next Steps</h3>
          <ul style="color: #eee; margin: 0; padding-left: 20px;">
            ${data.next_steps.split('\n').filter(l => l.trim()).map(line => 
              `<li>${line.trim().replace(/^[-•]/, '').trim()}</li>`
            ).join('')}
          </ul>
        </div>
      `
    },
    {
      title: "Timeline",
      content: `
        <div style="padding: 15px;">
          <h3 style="color: #7C3AED; margin-bottom: 10px;">Timeline</h3>
          <p style="color: #ddd; margin: 10px 0;">
            <strong>${data.timeline.start_date}</strong> → <strong>${data.timeline.end_date}</strong>
          </p>
          <div style="background: #4B5C6D; height: 30px; border-radius: 5px; margin: 15px 0; position: relative; border: 2px solid #7C3AED;">
            ${data.timeline.milestones.slice(0, 3).map((m, i) => `
              <div style="position: absolute; left: ${20 + i * 25}%; top: -10px; width: 30px; height: 50px; text-align: center;">
                <div style="width: 10px; height: 10px; background: #7C3AED; border-radius: 50%; margin: 0 auto; border: 2px solid #fff;"></div>
                <p style="font-size: 10px; color: #ddd; margin: 5px 0 0 0;">${m.label}</p>
              </div>
            `).join('')}
          </div>
        </div>
      `
    }
  ];

  container.innerHTML = `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
      ${slides.map((slide, idx) => `
        <div style="
          background: #2A2A3E;
          border: 2px solid #7C3AED;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        ">
          <div style="background: #1E1E2E; padding: 10px; border-bottom: 2px solid #7C3AED;">
            <h4 style="color: #7C3AED; margin: 0; font-size: 14px;">Slide ${idx + 1}: ${slide.title}</h4>
          </div>
          <div style="height: 150px; overflow: hidden; font-size: 12px;">
            ${slide.content}
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

// Call the function when page loads (if data is injected as window.slideData)
if (window.slideData) {
  renderSlidePreview(window.slideData, 'slide-preview-container');
}
</script>

(() => {
  'use strict';
  const samples = window.HomepageSamples || {};
  const track = (name, properties) => window.nomadAgentAnalytics?.track(name, properties);
  const element = (tag, value, className) => {
    const el = document.createElement(tag);
    if (value !== undefined) el.textContent = value;
    if (className) el.className = className;
    return el;
  };
  const shown = value => value === null || value === undefined || value === '' ? 'Unknown' : value;
  const readableDate = value => {
    if (!value) return 'Unknown';
    const date = new Date(value);
    return Number.isNaN(date.valueOf()) ? 'Unknown' : new Intl.DateTimeFormat('en-GB', {day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}).format(date);
  };
  const copy = async value => {
    if (navigator.clipboard?.writeText) return navigator.clipboard.writeText(value);
    throw new Error('Clipboard is unavailable');
  };

  document.querySelectorAll('[data-output-explorer]').forEach(explorer => {
    const actor = explorer.querySelector('[data-output-actor]');
    const format = explorer.querySelector('[data-output-format]');
    const preview = explorer.querySelector('[data-output-preview]');
    const note = explorer.querySelector('[data-output-note]');
    const status = explorer.querySelector('[data-output-status]');
    let key = 'euraxess';
    const fields = () => {
      const sample = samples[key];
      if (key === 'scorer') return {title:sample.record.role,company:sample.record.company,location:'Fictional role',deadline:'Not applicable'};
      const d = sample.record.data;
      return {title:sample.shortTitle,company:shown(d.company.name),location:shown(d.locations?.[0]?.raw),deadline:readableDate(d.application.deadline)};
    };
    const card = () => {
      const sample = samples[key]; const f = fields();
      const card = element('article', undefined, 'output-record');
      card.append(element('p', sample.kind + (sample.date ? ' · ' + sample.date : ''), 'output-record-kind'));
      const heading = element('div', undefined, key === 'scorer' ? 'fit-heading' : '');
      heading.append(element('h3', f.title));
      if (key === 'scorer') {
        const score = element('strong', String(sample.record.fitScore), 'fit-number');
        score.append(element('small', '/100')); heading.append(score);
      }
      card.append(heading, element('p', f.company, 'sample-company'));
      const rows = key === 'scorer'
        ? [['Delivery score',sample.record.deliveryScore + ' / 5'],['Matched skills',sample.record.candidate.skills.join(' · ')],['Needs review',sample.record.gaps[0]]]
        : [['Location',f.location],[key === 'euraxess' ? 'Research fields' : 'Work arrangement',key === 'euraxess' ? 'Materials engineering' : shown(sample.record.data.employment.workArrangements?.join(', '))],['Application deadline',f.deadline]];
      const dl = element('dl');
      rows.forEach(([label,value]) => {
        const row = element('div'); const dd = element('dd', value);
        if (key === 'euraxess' && label === 'Application deadline') dd.append(element('small','22:59:59 UTC'));
        row.append(element('dt', label), dd); dl.append(row);
      });
      card.append(dl);
      if (key === 'scorer') {
        const list = element('ul', undefined, 'fit-evidence');
        sample.record.evidence.forEach(reason => list.append(element('li', reason))); card.append(list);
      }
      return card;
    };
    const table = () => {
      const f = fields(); const t = element('table');
      t.append(element('caption', samples[key].kind + ' · ' + samples[key].actorLabel));
      const thead = element('thead'); const heading = element('tr');
      const labels = key === 'scorer' ? ['Role','Company','Fit','Delivery'] : ['Job','Company','Location','Deadline'];
      labels.forEach(label => {const th=element('th',label);th.scope='col';heading.append(th);});
      thead.append(heading);t.append(thead);
      const body = element('tbody'); const row = element('tr');
      const values = key === 'scorer' ? [f.title,f.company,samples[key].record.fitScore+' / 100',samples[key].record.deliveryScore+' / 5'] : [f.title,f.company,f.location,f.deadline];
      values.forEach(value => row.append(element('td',value)));body.append(row);t.append(body);
      return t;
    };
    const render = () => {
      preview.replaceChildren();
      if (format.value === 'json') {
        const pre=element('pre');pre.append(element('code',JSON.stringify(samples[key].record,null,2)));preview.append(pre);
      } else if (format.value === 'table') preview.append(table());
      else preview.append(card());
      preview.scrollTop=0;preview.scrollLeft=0;
      note.textContent=samples[key].note;
      const json=explorer.querySelector('[data-download-json]');json.href='/samples/explorer/'+key+'.json';json.dataset.product=key;
      const csv=explorer.querySelector('[data-download-csv]');csv.hidden=key==='scorer';csv.href='/samples/explorer/'+key+'.csv';csv.dataset.product=key;
      const source=explorer.querySelector('[data-output-source]');source.hidden=!samples[key].sourceUrl;
      if(samples[key].sourceUrl) source.href=samples[key].sourceUrl;
      explorer.querySelector('[data-output-format-note]').textContent=key==='scorer' ? 'Fictional preview; not the canonical fit schema.' : 'CSV is a flat projection. JSON keeps every field.';
    };
    actor.addEventListener('change', () => {
      if(!Object.hasOwn(samples,actor.value)) return;
      key=actor.value;render();status.textContent=samples[key].actorLabel+' · '+samples[key].kind.toLowerCase()+'.';
      track('sample_source_selected',{product:key,format:format.value,placement:explorer.dataset.outputExplorer});
    });
    format.addEventListener('change', () => {
      render();status.textContent='Showing '+format.selectedOptions[0].textContent+' for '+samples[key].actorLabel+'.';
      track('sample_view',{product:key,format:format.value,placement:explorer.dataset.outputExplorer});
    });
    explorer.querySelector('[data-copy-output]').addEventListener('click', async () => {
      try {
        await copy(JSON.stringify(samples[key].record,null,2));status.textContent='JSON copied.';
        track('sample_copied',{product:key,format:'json',placement:explorer.dataset.outputExplorer});
      } catch {
        format.value='json';render();preview.focus();status.textContent='Select and copy the JSON below, or use Download JSON.';
      }
    });
    if(samples[key]) render();
  });

  const calculator=document.querySelector('[data-trial-calculator]');
  if(calculator) {
    const tool=calculator.querySelector('[data-trial-tool]');
    const count=calculator.querySelector('[data-trial-count]');
    const output=calculator.querySelector('[data-trial-total]');
    const update=() => {
      const amount=Number(count.value);const valid=count.value!=='' && Number.isInteger(amount) && amount>=1 && amount<=1000000;
      count.setAttribute('aria-invalid',String(!valid));output.classList.toggle('invalid',!valid);
      if(!valid) {output.textContent='Enter 1–1,000,000 results';return;}
      const total=amount*(tool.value==='scorer'?.02:.0009);
      output.textContent='$'+total.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:total<.01?4:2});
    };
    count.addEventListener('input',update);tool.addEventListener('change',update);
    calculator.querySelectorAll('[data-trial-preset]').forEach(button=>button.addEventListener('click',()=>{count.value=button.dataset.trialPreset;update();}));
    update();
  }
})();

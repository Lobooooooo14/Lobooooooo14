<div align="center">
  <h3>👋 Hi, I'm {{ gh_name }}</h3>
  
  <p>🐺 Hi, my name is Gabriel Lobo</p>
  <p>🧔 I'm {{ '2006-07-02' | age }} years oldㅤㅤㅤㅤㅤㅤ</p>
  <p>🧠 I'm a technology enthusiast</p>

  <br/>

  <img width="600" alt="Skills / cool things" src="https://skills-icons.vercel.app/api/icons?i=python,md,html,css,js,github,git,vscode,linux,node,ts,sass,react,vite,vercel,lottie,ionic,capacitor,zustand,framer,firebase,arduino,godot,tailwind,shadcnui,lucide,zorinos,pnpm,reactnative&perline=14" />
</div>

<hr />

{% if followers|length > 0 %}
<div align="center">
    <h4>👤 Followers 👤</h4>
    <p><i>Want to participate? just follow me!</i></p>
    <img width="600" src=".github/assets/cards/top3.svg" alt="Top 3 followers contributors (monthly)" />
    {% if followers|length > 2 and total_contributions > 0 %}
    <details>
    <summary>Leaderboard</summary>
    <br/>
    <table>
        <thead>
            <tr align="center">
                <th>Position</th>
                <th>Follower</th>
                <th>Contributions</th>
            </tr>
        </thead>
        <tbody>
            {% for position, name, url, contributions in followers %}
            {% if contributions > 0 %}
            <tr align="center">
                <td>{{ position + 1 }}°</td>
                <td><a href="{{ url }}">{{ name }}</a></td>
                <td>{{ contributions }} ctr.</td>
            </tr>
            {% endif %}
            {% endfor %}
        </tbody>
    </table>
    </details>
    {% endif %}
</div>
{% endif %}

<div align="center">
  <h4>🐍 Snakommits 🐍</h4>
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Lobooooooo14/Lobooooooo14/snake-output/snake-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Lobooooooo14/Lobooooooo14/snake-output/snake-light.svg">
      <img alt="github contribution grid snake animation" src="https://raw.githubusercontent.com/Lobooooooo14/Lobooooooo14/snake-output/snake-light.svg">
    </picture>
</div>

<h6 align="right">
  This profile is updated every day!<br/> <i>{{ last_update }}</i>
<h6>

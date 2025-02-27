import express from 'express';
import mysql from 'mysql2';

const app = express();
const port = 8000;

// 创建数据库连接
const db = mysql.createConnection({
  host: 'localhost',
  user: 'lipeng',
  password: '1q2w3e',
  database: 'product_iteration'
});

// 连接到数据库
db.connect((err) => {
  if (err) throw err;
  console.log('Connected to database');
});

// API 端点
app.get('/api/product321', (req, res) => {
  const query = `
    SELECT 
      p.department AS departmentName,
      p.id AS projectId,
      p.project_name AS projectName,
      p.project_code AS projectCode,
      v.version_name AS versionName,
      v.release_date AS releaseDate,
      v.status AS versionStatus,
      s.sprint_name AS iterationName,
      s.end_time AS iterationReleaseDate,
      s.status AS iterationStatus,
      r.issue_type AS issueType,
      r.title AS issueTitle,
      r.number AS issueNumber,
      r.priority_cn AS issuePriority,
      r.status_cn AS issueStatus,
      r.created_user_display_name AS issueCreator,
      r.issue_id AS issueId,
      r.id AS issueIndexId,
      r.current_sprint AS issueVersion,
      r.current_version AS issueIteration
    FROM products_localproject p
    LEFT JOIN products_localversion v ON p.id = v.project_id
    LEFT JOIN products_localsprint s ON p.id = s.project_id
    LEFT JOIN products_localrequirement r ON v.version_name = r.current_sprint OR s.sprint_name = r.current_version
    ORDER BY p.department, p.project_name, v.version_name, s.sprint_name;
  `;

  db.query(query, (err, results) => {
    if (err) {
      console.error('Error fetching data:', err);
      return res.status(500).json({ error: 'Database query failed' });
    }

    // 组织数据
    const departments = {};
    results.forEach(row => {
      const { departmentName, projectId, projectName, projectCode, versionName, releaseDate, versionStatus, iterationName, iterationReleaseDate, iterationStatus, issueType, issueTitle, issueNumber, issuePriority, issueStatus, issueCreator, issueId, issueIndexId, issueVersion, issueIteration } = row;

      // 初始化部门
      if (!departments[departmentName]) {
        departments[departmentName] = {
          departmentName,
          projects: []
        };
      }

      // 初始化项目空间
      let project = departments[departmentName].projects.find(p => p.projectId === projectId);
      if (!project) {
        project = {
          projectId,
          projectName,
          projectCode,
          versions: [],
          iterations: []
        };
        departments[departmentName].projects.push(project);
      }

      // 添加版本
      if (versionName) {
        const version = {
          versionName,
          releaseDate,
          versionStatus,
          issues: []
        };
        project.versions.push(version);
      }

      // 添加迭代
      if (iterationName) {
        const iteration = {
          iterationName,
          iterationReleaseDate,
          iterationStatus,
          issues: []
        };
        project.iterations.push(iteration);
      }

      // 添加问题
      const issue = {
        issueType,
        issueTitle,
        issueNumber,
        issuePriority,
        issueStatus,
        issueCreator,
        issueId,
        issueIndexId,
        issueVersion,
        issueIteration
      };

      // 将问题添加到对应的版本或迭代
      if (versionName) {
        const version = project.versions.find(v => v.versionName === versionName);
        if (version) {
          version.issues.push(issue);
        }
      }
      if (iterationName) {
        const iteration = project.iterations.find(i => i.iterationName === iterationName);
        if (iteration) {
          iteration.issues.push(issue);
        }
      }
    });

    // 返回结果
    res.json(Object.values(departments));
  });
});

// 启动服务器
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
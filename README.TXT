AccessUTI

Sistema Web de Gestión de Usuarios de Red

Proyecto desarrollado en Python (Flask) para la gestión y monitoreo de usuarios de red institucionales, integrando:
	•	CRUD de usuarios
	•	Control de permisos especiales
	•	Gestión de VPN
	•	Estados (ACTIVE / INACTIVE)
	•	Dashboard dinámico con amCharts
	•	Implementación académica de estructuras de datos (BST, LinkedList, Stack)

⸻
Objetivo del Proyecto

Diseñar e implementar un sistema web que permita:
	•	Centralizar la gestión de usuarios de red
	•	Controlar accesos especiales y VPN
	•	Visualizar métricas en tiempo real
	•	Aplicar estructuras de datos en un entorno real

Este proyecto combina conceptos de:
	•	Programación Web
	•	Estructuras de Datos
	•	Arquitectura MVC
	•	APIs REST
	•	Visualización de datos

⸻

🏗️ Arquitectura del Sistema

Backend
	•	Python 3.x
	•	Flask
	•	Jinja2
	•	Estructuras personalizadas:
	•	BST (Binary Search Tree)
	•	LinkedList
	•	Stack (auditoría)

Frontend
	•	HTML5
	•	CSS3 (diseño institucional claro)
	•	JavaScript
	•	amCharts 5

Visualización
	•	Column Charts
	•	Horizontal Bar Charts
	•	Donut Charts
	•	Datos consumidos desde endpoints JSON


AccessUTI/
│
├── app/
│   ├── routes/
│   │   ├── users.py
│   │   └── auth.py
│   │
│   ├── services/
│   │   └── user_service.py
│   │
│   ├── ds/                 # Estructuras de datos
│   │   ├── bst.py
│   │   ├── linked_list.py
│   │   └── stack.py
│   │
│   └── core/
│       ├── decorators.py
│       └── auth.py
│
├── templates/
│   ├── base.html
│   ├── login.html
│   └── dashboard.html
│
├── static/
│   └── styles.css
│
├── data/
│   └── usuarios.csv
│
├── app.py
└── README.md



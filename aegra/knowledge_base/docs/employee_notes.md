# Table: employee
## Notes
- Поле `salary` рассчитывается по формуле: base_salary * experience_factor + bonus
- Удалённые сотрудники не удаляются из таблицы, а помечаются через `employment_status = 'terminated'`
- Поле `full_name` формируется автоматически как `last_name + ' ' + first_name + ' ' + middle_name`
- Табельный номер `employee_number` должен быть уникальным в пределах компании
- История изменений должности и подразделения хранится в отдельной таблице `employee_history`
- Сотрудники на испытательном сроке имеют `probation_end_date` в будущем
- При увольнении сотрудника заполняется `termination_date` и `employment_status = 'terminated'`
from datetime import datetime


def payment(date_beg, date_end):
    payment_str = "declare @date_beg date,@date_end date set @date_beg = '{}' set @date_end = '{}' " \
                  "select EOMONTH(tr.TransactionDate) as 'Date', sum((case when tr.CurrencyID = 417 and " \
                  "tr.Comment like '%Погашение основного%' and acc_credit.BalanceGroup in (10915, 10917, 10921, 10923, 10932, 10934, 10938, 10940, 10944, 10712, 10922) then tr.SumV " \
                  "else 0 end)) as 'Pay417', sum((case when tr.CurrencyID = 840 and " \
                  "tr.Comment like '%Погашение основного%' and acc_credit.BalanceGroup in (10915, 10917, 10921, 10923, 10932, 10934, 10938, 10940, 10944, 10712, 10922) then tr.SumV " \
                  "else 0 end)) as 'Pay840', sum((case when tr.CurrencyID = 417 and " \
                  "tr.Comment like '%процент%' and tr.Comment like '%погаш%' and (acc_credit.BalanceGroup like '119%' or acc_credit.BalanceGroup like '118%') then tr.SumV " \
                  "else 0 end)) as 'Proc417', sum((case when tr.CurrencyID = 840 and " \
                  "tr.Comment like '%процент%' and tr.Comment like '%погаш%' and (acc_credit.BalanceGroup like '119%' or acc_credit.BalanceGroup like '118%') then tr.SumV " \
                  "else 0 end)) as 'Proc840' " \
                  "from dbo.Transactions as tr inner join dbo.Accounts as acc_credit on (tr.CreditAccountID = acc_credit.AccountNo) " \
                  "where tr.TransactionDate between @date_beg and @date_end group by EOMONTH(tr.TransactionDate) order by EOMONTH(tr.TransactionDate)".format(
        date_beg, date_end)
    return payment_str


def payment_purpose(date_beg, date_end):
    payment_purpose_str = "declare @date_beg date,@date_end date set @date_beg = '{}' set @date_end = '{}' " \
                          "select p.TypeName as 'Purpose', sum((case when tr.CurrencyID = 417 and tr.Comment like '%Погашение основного%' " \
                          "and acc_credit.BalanceGroup in (10915, 10917, 10921, 10923, 10932, 10934, 10938, 10940, 10944, 10712, 10922) " \
                          "then tr.SumV else 0 end)) as 'Pay417', sum((case when tr.CurrencyID = 840 and tr.Comment like '%Погашение основного%' " \
                          "and acc_credit.BalanceGroup in (10915, 10917, 10921, 10923, 10932, 10934, 10938, 10940, 10944, 10712, 10922) then tr.SumV " \
                          "else 0 end)) as 'Pay840', sum((case when tr.CurrencyID = 417 and tr.Comment like '%процент%' " \
                          "and tr.Comment like '%погаш%' and (acc_credit.BalanceGroup like '119%' or acc_credit.BalanceGroup like '118%') then tr.SumV " \
                          "else 0 end)) as 'Proc417', sum((case when tr.CurrencyID = 840 and tr.Comment like '%процент%' and tr.Comment like '%погаш%' " \
                          "and (acc_credit.BalanceGroup like '119%' or acc_credit.BalanceGroup like '118%') then tr.SumV else 0 end)) as 'Proc840' " \
                          "from dbo.Transactions as tr inner join dbo.Accounts as acc_credit on (tr.CreditAccountID = acc_credit.AccountNo) " \
                          "left join [Credits].[CreditsAccounts] as ca on tr.CreditAccountID = ca.AccountNo and tr.CurrencyID = ca.CurrencyID " \
                          "left join [Credits].[Histories] as h on ca.CreditID = h.CreditID left join [Credits].[Purposes] as p on h.LoanPurposeTypeID = p.TypeID " \
                          "where tr.TransactionDate between @date_beg and @date_end group by p.TypeName order by p.TypeName".format(
        date_beg, date_end)
    return payment_purpose_str


def overdue(date_beg, date_end):
    overdue_str = "declare @date_beg date, @date_end date set @date_beg = '{}' set @date_end = '{}' " \
                  "SELECT CONCAT (h.CreditID, '/1') as 'number', case when c.CompanyName is Null then CONCAT(c.Surname,' ',c.CustomerName,' ',c.Otchestvo) " \
                  "when c.Surname is Null and c.CustomerName is null and c.Otchestvo is null then c.CompanyName end as 'ClientName', " \
                  "convert(varchar, c.DateOfBirth, 104) as 'birth_date', CONCAT (c.DocumentSeries,c.DocumentNo) as 'passport', c.IdentificationNumber as 'inn', " \
                  "x.MainSummStartOverdueDate as 'start_overdue', x.date as 'end_overdue', x.MainSummOverdueDays as 'overdue_days', x.MainOverdueSumm as 'main_overdue_summ', " \
                  "u.Fullname as 'user', p.Name as 'product', a.AccountNo as 'account_no', a.CurrentBalance as 'current_balance', a.CurrentNationalBalance as 'current_nat_balance' " \
                  "FROM(select	y.CreditID, y.date, y.MainSummStartOverdueDate, ho.MainSummOverdueDays, ho.MainOverdueSumm from (select CreditID, MainSummStartOverdueDate, " \
                  "max(OperationDate) as 'date' from [Credits].[HistoriesOverdues] where MainSummOverdueDays > 0 and OperationDate between @date_beg and @date_end " \
                  "group by CreditID, MainSummStartOverdueDate) as y left join [Credits].[HistoriesOverdues] as ho on y.CreditID = ho.CreditID " \
                  "and y.MainSummStartOverdueDate=ho.MainSummStartOverdueDate and y.date = ho.OperationDate) as x left join [Credits].[Histories] as h " \
                  "on x.CreditID = h.CreditID left join [Credits].[HistoriesCustomers] as hc on x.CreditID = hc.CreditID left join [dbo].[Customers] as c " \
                  "on hc.CustomerID = c.CustomerID left join [Credits].[HistoriesOfficers] as ho on x.CreditID = ho.CreditID left join [dbo].[Users] as u " \
                  "on ho.UserID = u.UserID left join [Credits].[Products] as p on h.ProductID = p.ProductID left join [Credits].[CreditsAccounts] as ca " \
                  "on x.CreditID = ca.CreditID left join [dbo].[Accounts] as a on ca.AccountNo = a.AccountNo where (ho.EndDate is Null or ho.EndDate > @date_end) " \
                  "and a.BalanceGroup like '%2140%' order by h.AgreementNo".format(date_beg, date_end)
    return overdue_str


def verification(client_name, date_beg, date_end, verificated, risk):
    verification_str = "declare @date_beg date, @date_end date set @date_beg = '{1}' set @date_end = '{2}'" \
                       "SELECT c.CustomerID, case when c.CompanyName is Null then CONCAT(c.Surname,' ',c.CustomerName,' ',c.Otchestvo) " \
                       "when c.Surname is Null and c.CustomerName is null and c.Otchestvo is null then c.CompanyName end as 'ClientName', " \
                       "v.VerificationDate, case when v.VerificatorTypeId = 1 then 'Контролер' when v.VerificatorTypeId = 2 then 'Офицер Комплаенс' " \
                       "else 'Неизвестно' end as 'Inspector', u.Fullname as 'Verificator', case when v.RiskTypeID = 3 then 'Средний' " \
                       "when v.RiskTypeID = 2 then 'Высокий' when v.RiskTypeID = 1 then 'Низкий' else 'Неизвестно' end as 'Risk', " \
                       "case when v.VerificationDate is Null and v.UserID is Null then 'Не идентифицирован' when v.VerificationDate is not Null and v.UserID is not Null then " \
                       "case when t.VerificatorTypeId = 2 then 'Да' else 'Нет' end else Null end as 'Verificated' FROM dbo.Customers as c " \
                       "left join [dbo].[Verifications] as v on v.CustomerID = c.CustomerID " \
                       "left join dbo.Users as u on v.UserID = u.UserID left join (select * from [dbo].[Verifications] where VerificatorTypeId = 2) as t on c.CustomerID = t.CustomerID" \
                       "where case when c.CompanyName is Null then CONCAT(c.Surname,' ',c.CustomerName,' ',c.Otchestvo) " \
                       "when c.Surname is Null and c.CustomerName is null and c.Otchestvo is null then c.CompanyName end like '%{0}%' and (v.VerificationDate between @date_beg and @date_end " \
                       "or v.VerificationDate is Null) and case when v.VerificationDate is Null and v.UserID is Null then 'Не идентифицирован' when v.VerificationDate is not Null and v.UserID is not Null then " \
                       "case when t.VerificatorTypeId = 2 then 'Да' else 'Нет' end else Null end like '%{3}%' and RiskTypeID in ({4}) order by Verificated, c.CustomerID".format(client_name, date_beg, date_end, verificated, risk)
    return verification_str

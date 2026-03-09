from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors

doc = SimpleDocTemplate("hr_policy.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

title_style = ParagraphStyle('Title', fontSize=18, fontName='Helvetica-Bold',
                              spaceAfter=20, textColor=colors.HexColor("#1F4E79"))
heading_style = ParagraphStyle('Heading', fontSize=13, fontName='Helvetica-Bold',
                                spaceAfter=10, spaceBefore=15,
                                textColor=colors.HexColor("#2E75B6"))
body_style = ParagraphStyle('Body', fontSize=10, fontName='Helvetica',
                              spaceAfter=8, leading=16)

def add(text, style):
    story.append(Paragraph(text, style))

def space():
    story.append(Spacer(1, 10))

# ── Cover ──────────────────────────────────────────────────
add("HUMAN RESOURCES POLICY DOCUMENT", title_style)
add("Company: TechCorp International", body_style)
add("Version: 2.1  |  Effective Date: January 2024", body_style)
add("Department: Human Resources", body_style)
space()

# ── Section 1 ──────────────────────────────────────────────
add("1. SALARY AND COMPENSATION POLICY", heading_style)
add("1.1 Salary Structure", heading_style)
add("""All employees are classified into salary bands based on their job grade. 
The company follows a structured compensation framework with the following bands:
Band A (Entry Level): $20,000 - $45,000 per annum.
Band B (Mid Level): $45,000 - $75,000 per annum.
Band C (Senior Level): $75,000 - $120,000 per annum.
Band D (Executive Level): $120,000 - $250,000 per annum.""", body_style)

add("1.2 Salary Review Process", heading_style)
add("""Salary reviews are conducted annually in December. All employees who have 
completed at least 6 months of service are eligible for a salary review. 
Performance ratings directly influence salary increments as follows:
Outstanding Performance: 10-15% increment.
Exceeds Expectations: 7-10% increment.
Meets Expectations: 3-6% increment.
Below Expectations: 0% increment with a performance improvement plan.""", body_style)

add("1.3 Bonus Policy", heading_style)
add("""Annual bonuses are paid in March each year. Bonus eligibility requires 
a minimum of 12 months of continuous service. The bonus pool is calculated 
as 15% of the company annual profit. Individual bonus allocation is based on 
performance rating and salary band. Maximum bonus is capped at 25% of annual salary.""", body_style)
space()

# ── Section 2 ──────────────────────────────────────────────
add("2. LEAVE POLICY", heading_style)
add("2.1 Annual Leave", heading_style)
add("""All full-time employees are entitled to 21 days of annual leave per year. 
Leave entitlement increases with service length as follows:
0-2 years service: 21 days per year.
3-5 years service: 25 days per year.
6-10 years service: 28 days per year.
Above 10 years service: 30 days per year.
Annual leave must be approved by the direct manager at least 2 weeks in advance. 
A maximum of 5 days can be carried forward to the next calendar year.""", body_style)

add("2.2 Sick Leave", heading_style)
add("""Employees are entitled to 10 days of paid sick leave per year. 
A medical certificate is required for sick leave exceeding 2 consecutive days. 
Sick leave cannot be carried forward to the next year. 
Employees with more than 5 consecutive sick days must submit a fitness to work 
certificate before returning to the office.""", body_style)

add("2.3 Maternity and Paternity Leave", heading_style)
add("""Maternity leave entitlement is 26 weeks fully paid for employees with 
more than 1 year of service. Paternity leave entitlement is 2 weeks fully paid. 
Adoption leave follows the same policy as maternity leave. 
Leave must be applied for at least 8 weeks before the expected date.""", body_style)
space()

# ── Section 3 ──────────────────────────────────────────────
add("3. PERFORMANCE MANAGEMENT POLICY", heading_style)
add("3.1 Performance Review Cycle", heading_style)
add("""Performance reviews are conducted twice a year — mid-year in June and 
annual review in December. All employees must set SMART goals at the beginning 
of each year in January. Goals are reviewed and updated at the mid-year review. 
Performance ratings are on a 5-point scale from 1 (Below Expectations) 
to 5 (Outstanding).""", body_style)

add("3.2 Performance Improvement Plan", heading_style)
add("""Employees receiving a performance rating of 1 for two consecutive reviews 
will be placed on a formal Performance Improvement Plan (PIP). The PIP duration 
is 90 days with weekly check-ins with the manager and HR. Failure to meet PIP 
targets may result in termination of employment. Successful completion of PIP 
results in removal from the plan with no further action.""", body_style)
space()

# ── Section 4 ──────────────────────────────────────────────
add("4. REMOTE WORK POLICY", heading_style)
add("4.1 Remote Work Eligibility", heading_style)
add("""Employees who have completed their probation period of 6 months are eligible 
for remote work. A maximum of 3 days per week remote work is permitted for most roles. 
IT and Security roles require a minimum of 4 days in office per week. 
Executive level employees follow a flexible arrangement agreed with the CEO.""", body_style)

add("4.2 Remote Work Requirements", heading_style)
add("""Employees working remotely must be available during core hours of 10am to 3pm. 
A stable internet connection of minimum 20 Mbps is required. 
Company laptop must be used for all work — personal devices are not permitted 
for accessing company systems. VPN must be active at all times when accessing 
company resources remotely.""", body_style)
space()

# ── Section 5 ──────────────────────────────────────────────
add("5. DEPARTMENT SPECIFIC POLICIES", heading_style)
add("5.1 IT Department", heading_style)
add("""IT department employees receive an additional technology allowance of $1,500 
per year for home office equipment. Certification bonuses are provided for approved 
certifications: $500 for associate level, $1,000 for professional level, 
$2,000 for expert level certifications. On-call allowance of $200 per week is paid 
for employees on the on-call rotation.""", body_style)

add("5.2 Sales Department", heading_style)
add("""Sales employees receive a base salary plus commission structure. 
Commission is calculated as 5% of deals closed up to target, and 8% for deals 
above target. A quarterly bonus of $2,000 is paid for achieving 100% of sales target. 
Car allowance of $500 per month is provided for field sales roles.""", body_style)

add("5.3 Finance Department", heading_style)
add("""Finance employees are required to maintain relevant professional certifications. 
The company sponsors certification renewals up to $1,000 per year. 
Finance team members involved in year-end closing receive a $500 completion bonus. 
Overtime during audit periods is compensated at 1.5x the hourly rate.""", body_style)
space()

# ── Section 6 ──────────────────────────────────────────────
add("6. CONTACT AND ESCALATION", heading_style)
add("""For all HR policy queries contact hr@techcorp.com or call extension 4500. 
Policy exceptions must be approved by the HR Director and Department Head jointly. 
All policy violations should be reported to hr.compliance@techcorp.com. 
This document is reviewed and updated annually every January.""", body_style)

doc.build(story)
print("hr_policy.pdf created successfully!")

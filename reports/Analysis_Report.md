# Customer Retention & Churn Analysis — Report

## 1. Executive Summary

This project examines customer retention and churn patterns for a simulated subscription-based business. The analysis covers overall churn, customer lifetime value, signup cohorts, customer segments, and subscription plans.

The objective is to demonstrate how data analytics can help businesses understand customer behavior and develop strategies to improve retention.

## 2. Dataset and Methodology

The dataset was generated using Python and contains 2,000 simulated customers, along with monthly subscription activity records.

The analysis includes:
- Customer data exploration and quality checks.
- Churn and retention KPI calculations.
- Customer lifetime value analysis.
- Cohort retention analysis.
- Segment and subscription plan comparisons.
- Visualization of churn patterns and retention drivers.

**Data limitation:** The dataset is synthetic. Findings describe the generated sample and cannot be generalized to a real business without real customer data.

## 3. Key Performance Metrics

The notebook calculates:
- Total customer count.
- Number of churned and active customers.
- Overall churn rate and retention rate.
- Average customer lifetime.
- Average customer lifetime value.
- Total subscription revenue in the generated activity records.

Refer to the executed notebook for the actual numerical results. These values should be copied from the notebook output rather than estimated.

## 4. Cohort Analysis

Customers are grouped by their signup month to compare retention over time. The cohort heatmap presents retention percentages for different signup cohorts across successive months.

This analysis can help identify cohorts with relatively strong or weak retention and indicate where onboarding or engagement strategies may warrant further investigation.

## 5. Customer Segment and Plan Analysis

The analysis compares customer retention and churn across business segments and subscription plans.

The segment and plan summaries can help identify:
- Groups with comparatively high churn.
- Groups with stronger retention.
- Differences in customer lifetime value.
- Areas for further customer research.

Specific conclusions should be based on the actual tables and charts produced by the notebook.

## 6. Customer Lifetime Value

Customer lifetime value is estimated from the subscription revenue recorded for each customer in the generated activity data.

CLV comparisons help illustrate how customer duration and subscription revenue contribute to customer value. The estimates are based on the assumptions built into the synthetic dataset and are not forecasts of real-world revenue.

## 7. Churn Patterns and Retention Drivers

The churn visualizations examine the timing and distribution of churn events. Retention driver comparisons explore how observed retention differs across segments and plans.

These comparisons show associations within the simulated data. They do not establish that any particular factor causes churn.

## 8. Recommendations

Based on the analytical methods demonstrated, a subscription business could consider the following actions:

1. **Improve onboarding:** Review the early customer experience and identify points where customers may disengage.
2. **Monitor high-churn segments:** Investigate the needs and expectations of segments with lower observed retention.
3. **Review subscription plans:** Assess whether plan features and pricing match customer requirements.
4. **Track cohorts:** Monitor retention by signup month to evaluate changes in onboarding and customer engagement.
5. **Monitor customer value:** Use CLV alongside retention metrics when prioritizing customer success initiatives.

These are general recommendations for further investigation, not confirmed interventions from real customer data.

## 9. Limitations

- The dataset is synthetically generated.
- Churn events are simulated using assumptions in the Python script.
- The results may not reflect real subscription business behavior.
- Observed segment differences do not prove causation.
- The analysis should be validated against real business data before operational decisions are made.

## 10. Conclusion

This project demonstrates a structured workflow for customer retention and churn analysis using Python. It combines KPI calculations, cohort analysis, customer lifetime value estimates, segment comparisons, and visualizations to illustrate how customer analytics can support retention planning.

The project provides a foundation for further work using real customer data, improved churn definitions, and validated predictive models.

## Tools Used

Python, Jupyter Notebook, Pandas, NumPy, Matplotlib, Seaborn, and Plotly.

**Program:** Future Interns — Data Science & Analytics Internship  
**Task:** Task 2 — Customer Retention & Churn Analysis  
**CIN ID:** FIT/SEP26/DS23554
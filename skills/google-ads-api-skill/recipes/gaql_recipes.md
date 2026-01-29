# GAQL recipes

## 1) List campaigns
SELECT
  campaign.id,
  campaign.name,
  campaign.status
FROM campaign
ORDER BY campaign.id
LIMIT 50

## 2) Basic performance last 7 days
SELECT
  campaign.id,
  campaign.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros
FROM campaign
WHERE segments.date DURING LAST_7_DAYS
LIMIT 100

## 3) Search terms (example shape; confirm resource/fields in docs)
- Always confirm the correct view/resource + selectable fields using GoogleAdsFieldService.

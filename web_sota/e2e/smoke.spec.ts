import { expect, test } from "@playwright/test";

// Dashboard shell: hero, onboarding cue, KPI grid render without a backend.
test("dashboard renders hero and KPI grid", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("dashboard")).toBeVisible();
  await expect(page.getByTestId("kpi-grid")).toBeVisible();
  await expect(page.getByTestId("kpi-connection")).toBeVisible();
});

test("chat controls render with personalities and examples", async ({ page }) => {
  await page.goto("/chat");
  await expect(page.getByTestId("chat-page")).toBeVisible();
  await expect(page.getByTestId("chat-controls")).toBeVisible();
  await expect(page.getByTestId("personality-select")).toBeVisible();
  await expect(page.getByTestId("example-prompts")).toBeVisible();
  await expect(page.getByTestId("chat-input")).toBeVisible();
  await expect(page.getByTestId("chat-send")).toBeVisible();
});

test("skills and inbox pages render", async ({ page }) => {
  await page.goto("/skills");
  await expect(page.getByTestId("skills-page")).toBeVisible();
  await page.goto("/inbox");
  await expect(page.getByTestId("inbox-page")).toBeVisible();
});

# Human spot check

For each item, read the question, the reference, and the answer, then fill in YOUR score (1-5) using the same rubric as the judge (5 = correct and complete, 1 = wrong or wrongly 'don't know').

## 1. f06 (faq; tier=small; cache_hit=False)
**Question:** How do I turn on two-factor authentication?

**Reference:**
- Two-factor authentication: Enable two-factor authentication in Settings > Security. You can use an authenticator app or SMS codes. Save the 10 backup codes shown during setup. If you lose your device, use a backup code to sign in, then reconfigure 2FA.

**Answer:** To enable two‑factor authentication, go to **Settings > Security** in your StashBox account. Follow the prompts to set up 2FA using an authenticator app or SMS codes, and be sure to save the 10 backup codes that are displayed during the setup.

**Judge:** 4 - The answer is correct and covers the main setup steps, but it omits the specific instruction on what to do if the user loses their device (using a backup code to sign in and reconfigure).

**Your score:** ___

## 2. h05 (hard; tier=large; cache_hit=False)
**Question:** Walk me through securing our team account step by step, including authentication, encryption and permissions.

**Reference:**
- Two-factor authentication: Enable two-factor authentication in Settings > Security. You can use an authenticator app or SMS codes. Save the 10 backup codes shown during setup. If you lose your device, use a backup code to sign in, then reconfigure 2FA.
- Encryption and security: Files are encrypted with AES-256 at rest and TLS 1.3 in transit. StashBox holds the encryption keys by default. Team plans can enable customer-managed keys so only your organization can decrypt data.
- Single sign-on: SAML single sign-on is available on the Team plan. Admins configure it in Admin console > Security with an identity provider such as Okta or Azure AD. SCIM user provisioning is also supported.
- Folder permissions for teams: Team admins can share folders with specific members as Viewer, Editor or Owner. Viewers can download, Editors can upload and rename, and Owners can manage permissions and delete. Permissions inherit down to subfolders unless overridden.

**Answer:** Here’s a step‑by‑step walk‑through of how to lock down a Team‑plan workspace in StashBox, using only the features described in the provided documentation:

---

### 1. Choose the Data‑region for the workspace  
1. When you **create** the Team workspace, select the region where you want all data stored – **US, EU, or India**.  
2. Remember that this choice is permanent; you can’t change the region later.  

---

### 2. Set up Strong Authentication  

#### a. Enable Two‑Factor Authentication (2FA) for all users  
1. In **Settings > Security**, turn on 2FA.  
2. Each user can pick either an authenticator app (Google Authenticator, Authy, etc.) or SMS codes.  
3. During setup the system shows **10 backup codes** – have every user **save these securely** (e.g., in a password manager).  
4. If a user loses their device, they can sign in with a backup code and then re‑configure 2FA.

#### b. (Optional but recommended) Configure SAML Single Sign‑On  
1. In the **Admin console > Security** section, add your identity provider (Okta, Azure AD, etc.).  
2. This makes login go through your corporate IdP, enforcing the same password policies and MFA you already use.  
3. SCIM provisioning is also available, so new employees are automatically created in StashBox and departing users are removed.

---

### 3. Harden Encryption  

1. By default all files are encrypted **AES‑256 at rest** and protected with **TLS 1.3 in transit** – no extra action needed.  
2. If you need full control over the keys, enable **customer‑managed keys** (available on Team plans). This makes only your organization able to decrypt the data; StashBox no longer holds the keys.  

---

### 4. Invite Users and Assign Roles  

1. In **Admin console > Users**, invite team members by entering their email addresses.  
2. When inviting, you can immediately assign them a role (Viewer, Editor, Owner) on the folders they’ll need.  

---

### 5. Configure Folder Permissions  

1. Go to the folder you want to protect and **share** it with specific members.  
2. Choose the appropriate permission level for each member:  

   * **Viewer** – can only download files.  
   * **Editor** – can upload new files, rename existing ones, and download.  
   * **Owner** – can do everything an Editor can, plus manage permissions and delete the folder.  

3. Permissions **inherit down** to all sub‑folders unless you explicitly override them on a sub‑folder.  
4. For highly sensitive data, give only **Owner** or **Editor** rights to a limited set of users and keep the rest as **Viewers**.

---

### 6. Ongoing Management  

* **Removing a member**: In **Admin console > Users**, delete the user. Access is revoked instantly.  
* **Data after removal**: Within **30 days** you can transfer that user’s files to another account; after that the files are permanently deleted.  

---

### Summary Checklist  

| Step | Action | Where |
|------|--------|-------|
| Choose region | Select US/EU/India at workspace creation | Workspace creation screen |
| Enable 2FA | Turn on, save backup codes | Settings > Security |
| (Optional) SAML SSO | Connect Ok

**Judge:** 2 - The answer includes significant unsupported details such as data regions (US/EU/India), specific user management actions (deleting users, 30-day retention), and specific app names that are not present in the reference documents.

**Your score:** ___

## 3. h10 (hard; tier=large; cache_hit=False)
**Question:** Compare the support options and data residency across all plans, and recommend what a healthcare startup should choose.

**Reference:**
- Contacting support: Free users get help through the community forum. Pro users get email support with a response within 24 hours. Team users get priority email and chat support with a response within 4 hours on business days.
- Data residency: Team plan customers can choose to store data in the US, EU or India regions. The region is chosen when the workspace is created and cannot be changed afterwards. Free and Pro accounts are stored in the US region.
- Compliance certifications: StashBox is SOC 2 Type II and ISO 27001 certified. Team plans can sign a data processing agreement for GDPR. We do not currently offer HIPAA business associate agreements.

**Answer:** **Data residency**

- **Free and Pro plans** – All data is stored in the **US** region.  
- **Team plan** – When the workspace is created you can pick the data‑storage region: **US, EU, or India**. After the workspace is created the region cannot be changed.

**Support options**

The only support‑related detail in the provided context is that past invoices can be re‑issued through support. No other information about support channels, response times, or plan‑specific support tiers is given.

**Recommendation for a healthcare startup**

- A healthcare startup typically needs strong compliance guarantees (e.g., HIPAA). StashBox **does not offer HIPAA Business Associate Agreements**, so it cannot meet HIPAA requirements regardless of the plan chosen.  
- If the startup’s primary concern is data‑residency and GDPR‑related processing, the **Team plan** is the only option that lets you store data outside the US (EU or India) and also allows you to sign a GDPR Data Processing Agreement.

**Conclusion**

Given the lack of HIPAA coverage, StashBox is not suitable for a healthcare startup that must comply with HIPAA. If the startup’s compliance needs are limited to GDPR and it wants control over where its data resides, the **Team plan** (choosing the EU region) would be the appropriate choice. Otherwise, a different provider that offers HIPAA BAAs should be considered.

**Judge:** 2 - The answer incorrectly claims that no support information is provided in the context, despite the reference documents explicitly detailing support channels and response times for Free, Pro, and Team plans.

**Your score:** ___

## 4. p02 (paraphrase; tier=small; cache_hit=False)
**Question:** I want to end my StashBox plan. What are the steps?

**Reference:**
- Cancel a subscription: To cancel, go to Settings > Billing > Cancel plan. Your plan stays active until the end of the current billing period. Your files remain accessible in read-only mode for 60 days after cancellation, then they are permanently deleted.

**Answer:** To end your StashBox plan and stop future charges, follow these steps:

1. **Log in** to your StashBox account.  
2. Go to **Account Settings** (usually found in the top‑right corner or in the sidebar).  
3. Find the **Subscription** or **Billing** section.  
4. Click **Cancel Subscription** (or a similarly named button).  
5. Confirm the cancellation when prompted.  

After you cancel, you’ll no longer be charged for the next billing cycle.  
If you cancel within 30 days of your last payment, you’ll receive a full refund to your original payment method within 5–7 business days. If you cancel after 30 days, no refund will be issued, but the plan will be terminated and you’ll keep access until the end of the current billing period.

**Judge:** 2 - The answer invents specific refund policies (30-day window, 5-7 business days) and navigation details not present in the reference, and omits the critical fact that files are deleted 60 days after cancellation.

**Your score:** ___

## 5. p10 (paraphrase; tier=cache; cache_hit=True)
**Question:** I accidentally deleted a document. Can I get it back?

**Reference:**
- Recover deleted files: Deleted files go to Trash and stay there for 30 days on Free and Pro, and 90 days on Team. To restore, open Trash, select the files and click Restore. After the retention period files are permanently deleted and cannot be recovered.

**Answer:** To recover a deleted file, open the **Trash** in StashBox, select the file(s) you want to restore, and click **Restore**. The file will be returned to its original location. (Note: files stay in Trash for 30 days on Free and Pro plans, and 90 days on Team.)

**Judge:** 4 - The answer is correct and includes the retention periods, but it omits the critical warning that files are permanently deleted and cannot be recovered after the retention period expires.

**Your score:** ___

## 6. p11 (paraphrase; tier=small; cache_hit=False)
**Question:** How far back can I restore older versions of a file?

**Reference:**
- Version history: StashBox keeps previous versions of edited files for 30 days on Free, 180 days on Pro and 365 days on Team. Open a file, choose Version history and click Restore on the version you want. Restoring creates a new version rather than overwriting.

**Answer:** You can restore older versions of a file up to the retention period for your plan:  
- **Free**: 30 days  
- **Pro**: 180 days  
- **Team**: 365 days  

Open the file, go to **Version history**, and click **Restore** on the desired version.

**Judge:** 4 - The answer correctly identifies the retention periods and the restoration steps, but it omits the detail that restoring a version creates a new version rather than overwriting the current one.

**Your score:** ___

## 7. p14 (paraphrase; tier=small; cache_hit=False)
**Question:** Is there a European data center option?

**Reference:**
- Data residency: Team plan customers can choose to store data in the US, EU or India regions. The region is chosen when the workspace is created and cannot be changed afterwards. Free and Pro accounts are stored in the US region.

**Answer:** Yes. Team‑plan customers can choose to store their data in the EU region when they create the workspace.

**Judge:** 4 - The answer is correct but omits the key constraint that the region cannot be changed after workspace creation.

**Your score:** ___

## 8. p18 (paraphrase; tier=small; cache_hit=False)
**Question:** How do I get a receipt for my payment?

**Reference:**
- Invoices and receipts: Download invoices from Settings > Billing > Invoices. Team admins can add a company name and tax ID that will appear on future invoices. Past invoices cannot be edited, but we can reissue one through support.

**Answer:** You can download a receipt (invoice) for your payment from the StashBox portal:

1. Log in to your account.  
2. Go to **Settings** → **Billing** → **Invoices**.  
3. Find the invoice that corresponds to your payment and download it.  

That invoice serves as the official receipt for your transaction. If you need a different format or a re‑issued copy, let me know and I can help you request it through support.

**Judge:** 4 - The answer correctly identifies the path to download invoices and mentions reissuing via support, but it omits the specific detail that team admins can add company name and tax ID to future invoices, which is part of the reference material.

**Your score:** ___

## 9. n05 (nearmiss; tier=small; cache_hit=False)
**Question:** How do I turn on single sign-on for my company?

**Reference:**
- Single sign-on: SAML single sign-on is available on the Team plan. Admins configure it in Admin console > Security with an identity provider such as Okta or Azure AD. SCIM user provisioning is also supported.

**Answer:** To enable single sign‑on (SSO) for your company on StashBox, follow these steps:

1. **Log in as an admin** to your StashBox account.  
2. Go to the **Admin console**.  
3. Navigate to **Security**.  
4. In the Security settings, you’ll find the option to **configure SAML single sign‑on**.  
5. Choose your identity provider (e.g., **Okta** or **Azure AD**) and follow the on‑screen instructions to complete the SAML setup.  

Once configured, users in your organization will be able to sign in via the chosen identity provider.

**Judge:** 4 - The answer correctly describes the configuration steps and providers but omits the requirement that SSO is available on the Team plan and the support for SCIM user provisioning.

**Your score:** ___

## 10. u04 (heldout; tier=small; cache_hit=False)
**Question:** Does annual billing save money?

**Reference:**
- Plans and pricing: StashBox has three plans. Free: 5 GB storage, 1 user. Pro: 2 TB storage, 1 user, 12 USD per month. Team: 5 TB storage per user, minimum 3 users, 20 USD per user per month. Annual billing gives a 20 percent discount.

**Answer:** I’m not sure.

**Judge:** 1 - The answer claims uncertainty despite the reference documents explicitly stating that annual billing provides a 20 percent discount.

**Your score:** ___

## 11. f14 (faq; tier=small; cache_hit=False)
**Question:** Can I store my data in the EU?

**Reference:**
- Data residency: Team plan customers can choose to store data in the US, EU or India regions. The region is chosen when the workspace is created and cannot be changed afterwards. Free and Pro accounts are stored in the US region.

**Answer:** Yes—if you’re on a Team plan, you can choose the EU region when you create the workspace. Free and Pro accounts are stored in the US by default, but Team plan customers can select EU (or India) and the data will stay there permanently.

**Judge:** 5 - The answer correctly identifies that Team plan customers can choose the EU region at workspace creation, while Free and Pro accounts are restricted to the US, matching the reference exactly.

**Your score:** ___

## 12. n06 (nearmiss; tier=small; cache_hit=False)
**Question:** How long are deleted files kept in Trash?

**Reference:**
- Recover deleted files: Deleted files go to Trash and stay there for 30 days on Free and Pro, and 90 days on Team. To restore, open Trash, select the files and click Restore. After the retention period files are permanently deleted and cannot be recovered.

**Answer:** Deleted files are kept in Trash for **30 days on Free and Pro plans, and 90 days on Team plans**.

**Judge:** 5 - The answer correctly states the retention periods for Free/Pro (30 days) and Team (90 days) plans as specified in the reference document.

**Your score:** ___

## 13. f12 (faq; tier=small; cache_hit=False)
**Question:** Is my data encrypted?

**Reference:**
- Encryption and security: Files are encrypted with AES-256 at rest and TLS 1.3 in transit. StashBox holds the encryption keys by default. Team plans can enable customer-managed keys so only your organization can decrypt data.

**Answer:** Yes. According to the information provided, your files are encrypted with AES‑256 while stored (at rest) and protected with TLS 1.3 during transfer (in transit).

**Judge:** 5 - The answer correctly identifies the encryption standards (AES-256 at rest and TLS 1.3 in transit) as stated in the reference document.

**Your score:** ___

## 14. u08 (heldout; tier=large; cache_hit=False)
**Question:** We deleted a project folder 45 days ago and the admin who owned it has left the company. Can we still get it back?

**Reference:**
- Recover deleted files: Deleted files go to Trash and stay there for 30 days on Free and Pro, and 90 days on Team. To restore, open Trash, select the files and click Restore. After the retention period files are permanently deleted and cannot be recovered.
- Add and remove team members: Admins invite members from Admin console > Users by entering email addresses. Removing a member revokes access immediately, and their files can be transferred to another user within 30 days before they are deleted.

**Answer:** If the folder was only moved to the Trash, its availability depends on the plan you’re on:

* **Free or Pro** – items stay in Trash for **30 days**. After that they are permanently deleted and cannot be recovered. Since the folder was deleted 45 days ago, it would already be gone on these plans.

* **Team** – items stay in Trash for **90 days**. In that case the folder is still within the retention window, so you can open the Trash, locate the folder and click **Restore** to get it back.

So you can recover the folder only if your account is on a **Team** plan; otherwise it’s no longer recoverable.

**Judge:** 4 - The answer correctly applies the Trash retention periods to determine recoverability but omits the specific detail from the reference that files of removed members can be transferred within 30 days, which is relevant context given the admin left the company.

**Your score:** ___

## 15. u01 (heldout; tier=small; cache_hit=False)
**Question:** Can I use Google Authenticator for 2FA?

**Reference:**
- Two-factor authentication: Enable two-factor authentication in Settings > Security. You can use an authenticator app or SMS codes. Save the 10 backup codes shown during setup. If you lose your device, use a backup code to sign in, then reconfigure 2FA.

**Answer:** Yes, you can use Google Authenticator for two‑factor authentication. The instructions in the settings allow any authenticator app, and Google Authenticator is a supported option.

**Judge:** 4 - The answer correctly confirms that an authenticator app can be used, which covers Google Authenticator, but it omits the specific setup instructions and backup code advice provided in the reference.

**Your score:** ___

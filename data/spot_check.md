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

**Answer:** Here’s a step‑by‑step guide to lock down a StashBox team account, using only the features described in the provided documentation:

---

### 1. Set Up Strong Authentication  

1. **Enable Two‑Factor Authentication (2FA)**  
   - Go to **Settings > Security**.  
   - Choose either an authenticator app (Google Authenticator, Authy, etc.) or SMS codes.  
   - Follow the prompts to scan the QR code and verify the code.  
   - **Save the 10 backup codes** that are shown during setup – you’ll need them if you lose the device.  

2. **(Optional for Team plans) Configure SAML Single Sign‑On**  
   - In the **Admin console > Security** section, select **SAML SSO**.  
   - Enter the details of your identity provider (e.g., Okta, Azure AD).  
   - Test the connection and enable it.  
   - This makes login require your corporate IdP, adding another layer of protection.  

3. **(Optional) Enable SCIM provisioning**  
   - If you want automatic user creation/deletion from your IdP, turn on **SCIM** in the same Security area.

---

### 2. Harden Data Encryption  

1. **At‑Rest Encryption** – All files are already encrypted with **AES‑256** when stored. No action is required.  

2. **In‑Transit Encryption** – All traffic uses **TLS 1.3** automatically.  

3. **Customer‑Managed Encryption Keys (optional, Team plans)**  
   - In the **Admin console**, locate the encryption settings.  
   - Switch from the default StashBox‑managed keys to **customer‑managed keys**.  
   - Upload or generate your own key material.  
   - From now on only your organization can decrypt the data, even if StashBox were compromised.

---

### 3. Configure Folder Permissions  

1. **Create the folder hierarchy** that matches your team’s structure (e.g., Projects → Dept A, Dept B, etc.).  

2. **Assign permissions** on each top‑level folder:  
   - **Viewer** – can only download files.  
   - **Editor** – can upload new files and rename existing ones.  
   - **Owner** – can manage permissions, add/remove members, and delete the folder.  

3. **Inheritance** – Permissions automatically flow down to sub‑folders unless you explicitly override them. Use overrides only when a sub‑folder needs a different access level.  

4. **Review regularly** – Periodically check the permission matrix to ensure only the right people have Owner or Editor rights.

---

### 4. Invite and Manage Team Members  

1. **Invite Users**  
   - Open **Admin console > Users**.  
   - Enter each member’s email address and send the invitation.  

2. **Assign Roles**  
   - After they accept, set each user’s role (Viewer/Editor/Owner) on the appropriate folders as described above.  

3. **Remove Users When Needed**  
   - To revoke access, select the user in **Admin console > Users** and choose **Remove**.  
   - Access is revoked immediately.  
   - Their files can be transferred to another user within **30 days**; after that the files are deleted.

---

### 5. Verify and Document  

1. **Test 2FA** – Log out and sign back in using the authenticator or a backup code.  
2. **Test S

**Judge:** 2 - The answer includes significant unsupported details such as specific UI paths for encryption, user management workflows, and a 30-day file retention policy that are not present in the reference documents.

**Your score:** ___

## 3. p02 (paraphrase; tier=small; cache_hit=False)
**Question:** I want to end my StashBox plan. What are the steps?

**Reference:**
- Cancel a subscription: To cancel, go to Settings > Billing > Cancel plan. Your plan stays active until the end of the current billing period. Your files remain accessible in read-only mode for 60 days after cancellation, then they are permanently deleted.

**Answer:** To end your StashBox plan and delete your account, follow these steps:

1. **Cancel the paid plan**  
   - Go to **Settings > Billing > Cancel plan**.  
   - Your plan will remain active until the end of the current billing period, and you’ll still have read‑only access to your files for 60 days after cancellation.

2. **Delete your account**  
   - After the plan is cancelled, go to **Settings > Account > Delete account**.  
   - This will permanently delete all your files, shared links, and version history after a 14‑day grace period.  
   - During those 14 days you can log in again to cancel the deletion if you change your mind.

That’s all you need to do to fully end your StashBox plan and remove your data.

**Judge:** 2 - The answer includes detailed steps for deleting the account (Settings > Account > Delete account, 14-day grace period) which are not present in the reference document, making it unsupported and potentially misleading.

**Your score:** ___

## 4. p10 (paraphrase; tier=cache; cache_hit=True)
**Question:** I accidentally deleted a document. Can I get it back?

**Reference:**
- Recover deleted files: Deleted files go to Trash and stay there for 30 days on Free and Pro, and 90 days on Team. To restore, open Trash, select the files and click Restore. After the retention period files are permanently deleted and cannot be recovered.

**Answer:** To recover a deleted file, open the **Trash** in StashBox, select the file(s) you want to restore, and click **Restore**. The file will be returned to its original location. (Note that files remain in Trash for 30 days on Free and Pro plans, and 90 days on Team.)

**Judge:** 4 - The answer is correct and includes the retention periods, but it omits the critical detail that files are permanently deleted and cannot be recovered after the retention period expires.

**Your score:** ___

## 5. p11 (paraphrase; tier=small; cache_hit=False)
**Question:** How far back can I restore older versions of a file?

**Reference:**
- Version history: StashBox keeps previous versions of edited files for 30 days on Free, 180 days on Pro and 365 days on Team. Open a file, choose Version history and click Restore on the version you want. Restoring creates a new version rather than overwriting.

**Answer:** You can restore older versions of a file up to the retention period for your plan:  
- **Free** – 30 days  
- **Pro** – 180 days  
- **Team** – 365 days  

Open the file, go to **Version history**, and click **Restore** on the desired version.

**Judge:** 4 - The answer correctly states the retention periods and restoration steps but omits the detail that restoring creates a new version rather than overwriting the current one.

**Your score:** ___

## 6. p16 (paraphrase; tier=cache; cache_hit=True)
**Question:** Can I access my files without internet?

**Reference:**
- Offline access: Mark files or folders as Available offline in the desktop or mobile app. They are downloaded and kept in sync when you reconnect. Offline files count against your local disk space, not your StashBox storage.

**Answer:** Yes. You can mark files or folders as “Available offline” in the desktop or mobile app. Once marked, they’ll be downloaded and kept in sync so you can access them even when you’re not connected.

**Judge:** 4 - The answer is correct and supported by the reference, but it omits the detail that offline files count against local disk space rather than StashBox storage.

**Your score:** ___

## 7. p18 (paraphrase; tier=small; cache_hit=False)
**Question:** How do I get a receipt for my payment?

**Reference:**
- Invoices and receipts: Download invoices from Settings > Billing > Invoices. Team admins can add a company name and tax ID that will appear on future invoices. Past invoices cannot be edited, but we can reissue one through support.

**Answer:** You can download a receipt (invoice) for your payment from the StashBox dashboard:

1. Log in and go to **Settings** → **Billing** → **Invoices**.  
2. Find the invoice that matches your payment and click **Download**.  

That PDF will serve as your receipt. If you need a different format or a re‑issued copy, let me know and I can help you request it through support.

**Judge:** 4 - The answer correctly identifies the path to download invoices and mentions reissuing via support, but it omits the specific detail that team admins can add company name and tax ID to future invoices, which is part of the reference material regarding invoice management.

**Your score:** ___

## 8. p19 (paraphrase; tier=small; cache_hit=False)
**Question:** Can I pay with UPI?

**Reference:**
- Accepted payment methods: We accept Visa, Mastercard, American Express and UPI for Indian customers. Team plans on annual billing can pay by bank transfer. Prepaid cards are not supported.

**Answer:** Yes, you can pay with UPI. The Team plan accepts Visa, Mastercard, American Express, and UPI for Indian customers.

**Judge:** 4 - The answer is correct but incorrectly implies that UPI is only available for the Team plan, whereas the reference states it is accepted for Indian customers generally.

**Your score:** ___

## 9. n05 (nearmiss; tier=small; cache_hit=False)
**Question:** How do I turn on single sign-on for my company?

**Reference:**
- Single sign-on: SAML single sign-on is available on the Team plan. Admins configure it in Admin console > Security with an identity provider such as Okta or Azure AD. SCIM user provisioning is also supported.

**Answer:** To enable single sign‑on for your company, you’ll need a Team plan. Once you’re on that plan, follow these steps:

1. Log in as an admin.  
2. Go to **Admin console** → **Security**.  
3. Choose **SAML single sign‑on** and configure it with your identity provider (e.g., Okta, Azure AD).  

That will activate SSO for your organization. If you need help setting up the identity provider or have any questions, let me know!

**Judge:** 4 - The answer correctly identifies the plan requirement and configuration steps but omits the mention of SCIM user provisioning support found in the reference.

**Your score:** ___

## 10. f12 (faq; tier=small; cache_hit=False)
**Question:** Is my data encrypted?

**Reference:**
- Encryption and security: Files are encrypted with AES-256 at rest and TLS 1.3 in transit. StashBox holds the encryption keys by default. Team plans can enable customer-managed keys so only your organization can decrypt data.

**Answer:** Yes. According to the information provided, all files are encrypted with AES‑256 while stored (at rest) and are protected with TLS 1.3 during transfer (in transit).

**Judge:** 4 - The answer correctly identifies the encryption standards (AES-256 at rest, TLS 1.3 in transit) but omits the details regarding key management (StashBox default vs. customer-managed keys) which are part of the security context in the reference.

**Your score:** ___

## 11. f18 (faq; tier=small; cache_hit=False)
**Question:** Where can I download invoices?

**Reference:**
- Invoices and receipts: Download invoices from Settings > Billing > Invoices. Team admins can add a company name and tax ID that will appear on future invoices. Past invoices cannot be edited, but we can reissue one through support.

**Answer:** You can download invoices from **Settings > Billing > Invoices**.

**Judge:** 5 - The answer correctly identifies the specific path to download invoices as stated in the reference document.

**Your score:** ___

## 12. f14 (faq; tier=small; cache_hit=False)
**Question:** Can I store my data in the EU?

**Reference:**
- Data residency: Team plan customers can choose to store data in the US, EU or India regions. The region is chosen when the workspace is created and cannot be changed afterwards. Free and Pro accounts are stored in the US region.

**Answer:** Yes—if you’re on a Team plan you can choose the EU region when you create the workspace. Free and Pro accounts are stored in the US by default, but Team plan customers can select EU (or India) at creation time.

**Judge:** 5 - The answer correctly identifies that Team plan customers can choose the EU region at workspace creation, while Free and Pro accounts are restricted to the US, matching the reference exactly.

**Your score:** ___

## 13. n07 (nearmiss; tier=small; cache_hit=False)
**Question:** How quickly does support respond to Pro users?

**Reference:**
- Contacting support: Free users get help through the community forum. Pro users get email support with a response within 24 hours. Team users get priority email and chat support with a response within 4 hours on business days.

**Answer:** Pro users receive email support with a response within **24 hours**.

**Judge:** 5 - The answer correctly identifies that Pro users receive email support with a response within 24 hours, which matches the reference document exactly.

**Your score:** ___

## 14. p07 (paraphrase; tier=small; cache_hit=False)
**Question:** Can I give someone access to a file through a URL?

**Reference:**
- Share files with a link: Right-click a file, choose Share, then Create link. You can set the link to view-only or edit, add a password, and set an expiry date. Anyone with the link can access the file until it expires or you disable the link.

**Answer:** Yes. You can right‑click a file, choose **Share → Create link**, and then give that link to anyone. The link can be set to view‑only or edit, and you can add a password or expiry date if you wish. Anyone with the link can access the file until it expires or you disable the link.

**Judge:** 5 - The answer accurately reflects all details from the reference document, including the steps to create the link and the available permissions and restrictions.

**Your score:** ___

## 15. h07 (hard; tier=large; cache_hit=False)
**Question:** An employee left the company. How do I remove their access and keep their files, and how long do I have?

**Reference:**
- Add and remove team members: Admins invite members from Admin console > Users by entering email addresses. Removing a member revokes access immediately, and their files can be transferred to another user within 30 days before they are deleted.
- Folder permissions for teams: Team admins can share folders with specific members as Viewer, Editor or Owner. Viewers can download, Editors can upload and rename, and Owners can manage permissions and delete. Permissions inherit down to subfolders unless overridden.

**Answer:** To remove the employee’s access:

1. **Open the Admin console** → **Users**.  
2. **Enter the employee’s email address** and use the **Remove** (or Delete) option. This revokes their access **immediately**.

**Keeping their files**

- After you remove the member, their files remain in the account.  
- You have **up to 30 days** to transfer those files to another user before the removed account (and its data) is automatically deleted.

So, delete the user now, and within the next 30 days move any needed files to another account. After that period the files will be removed permanently.

**Judge:** 5 - The answer correctly identifies the steps to remove a user via the Admin console, confirms immediate revocation of access, and accurately states the 30-day window to transfer files before deletion, matching all details in the reference documents.

**Your score:** ___

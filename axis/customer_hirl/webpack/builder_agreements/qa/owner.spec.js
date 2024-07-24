import { impersonate, menus, hasMenuLink } from '@/qaUtils'
import settings from './settings'

describe("Enrollment menu item ", () => {
  test('has company enrollment menu item', async (done) => {
    await impersonate(settings.ownerUsername)
    const item = await hasMenuLink(menus.TASKS, settings.OWNER_URL)
    await item.click()
    done()
  })
})

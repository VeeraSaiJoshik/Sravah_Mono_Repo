import {UserProfile} from  "../models/user"
import {Task} from  "../models/tasks"

export class BlockerPreview {
    blocker_id: string
    blocker_title: string

    associated_people: UserProfile[]
    associated_tasks: Task[]
    description: string
}
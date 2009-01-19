//
//  TaskViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TaskViewController.h"
#import "TaskDetailsController.h"

#import "TaskCell.h"
#import "CellFactory.h"

#import "TaskList.h"
#import "Database.h"
#import "Statement.h"

#import "Task.h"

#import "Configuration.h"

@implementation TaskViewController

- (void)loadData
{
	[headers release];
	
	TaskList *list;
	headers = [[NSMutableArray alloc] initWithCapacity:4];
	
	list = [[TaskList alloc] initWithView:@"OverdueTask" category:categoryId title:NSLocalizedString(@"Overdue", @"Overdue task title") status:TASKSTATUS_OVERDUE];
	if ([list count])
	{
		[headers addObject:list];
	}
	[list release];
	
	list = [[TaskList alloc] initWithView:@"DueTodayTask" category:categoryId title:NSLocalizedString(@"Due today", @"Due today task title") status:TASKSTATUS_DUETODAY];
	if ([list count])
	{
		[headers addObject:list];
	}
	[list release];
	
	list = [[TaskList alloc] initWithView:@"StartedTask" category:categoryId title:NSLocalizedString(@"Started", @"Started task title") status:TASKSTATUS_STARTED];
	if ([list count])
	{
		[headers addObject:list];
	}
	[list release];
	
	list = [[TaskList alloc] initWithView:@"NotStartedTask" category:categoryId title:NSLocalizedString(@"Not started", @"Not started task title") status:TASKSTATUS_NOTSTARTED];
	if ([list count])
	{
		[headers addObject:list];
	}
	[list release];
}

- initWithTitle:(NSString *)theTitle category:(NSInteger)theId
{
	if (self = [super initWithNibName:@"TaskView" bundle:[NSBundle mainBundle]])
	{
		title = [theTitle retain];
		categoryId = theId;

		[self loadData];
	}
	
	return self;
}

- (void)viewDidLoad
{
	self.navigationItem.title = title;
	self.navigationItem.rightBarButtonItem = [self editButtonItem];
}

- (void)childWasPopped
{
	[self loadData];
	[self.tableView reloadData];
}

- (void)dealloc
{
	[title release];
	[headers release];

    [super dealloc];
}

- (void)setEditing:(BOOL)editing animated:(BOOL)animated
{
	if ([headers count])
	{
		// See editingStyleForRowAtIndexPath. Without this trick, the first task
		// gets an Insert editing style as well as the newly-inserted row.

		isBecomingEditable = YES;

		[super setEditing:editing animated:animated];

		if (editing)
		{
			[self.tableView insertSections:[NSIndexSet indexSetWithIndex:0] withRowAnimation:UITableViewRowAnimationRight];
		}
		else
		{
			[self.tableView deleteSections:[NSIndexSet indexSetWithIndex:0] withRowAnimation:UITableViewRowAnimationRight];
		}
	}
	else
	{
		// There's a mess with the pseudo-section used when the data set is empty...
		[super setEditing:editing animated:animated];
		[self.tableView reloadData];
	}
}

- (void)onToggleTaskCompletion:(TaskCell *)cell
{
	NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
	NSInteger section, row;

	section = indexPath.section;
	row = indexPath.row;
	if (self.editing)
		section -= 1;

	Task *task = [[[headers objectAtIndex:section] taskAtIndex:row] retain];

	if ([task taskStatus] == TASKSTATUS_COMPLETED)
	{
		task.completionDate = nil;
		[task save];
	}
	else
	{
		[task setCompleted:YES];
		[task save];

		if (![Configuration configuration].showCompleted)
		{
			TaskList *list = [headers objectAtIndex:section];
			[list reload];
			
			if ([list count])
			{
				[self.tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationBottom];
			}
			else
			{
				[headers removeObjectAtIndex:section];
				[self.tableView deleteSections:[NSIndexSet indexSetWithIndex:indexPath.section] withRowAnimation:UITableViewRowAnimationBottom];
			}
		}
	}

	[cell setTask:task target:self action:@selector(onToggleTaskCompletion:)];
	[task release];

	tapping = [indexPath retain];
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
	NSInteger count = [headers count];

	if (self.editing)
	{
		return count + 1;
	}

    return count ? count : 1;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
	if (self.editing && (section == 0))
		return @"";

	if ([headers count])
	{
		return [[headers objectAtIndex:section - (self.editing ? 1 : 0)] title];
	}
	
	return NSLocalizedString(@"No tasks.", @"No tasks header");
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	if (self.editing && (section == 0))
		return 1;

	if ([headers count])
	{
		return [[headers objectAtIndex:section - (self.editing ? 1 : 0)] count];
	}
	
	return 0;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	UITableViewCell *cell;

	if (self.editing && (indexPath.section == 0))
	{
		cell = [tableView dequeueReusableCellWithIdentifier:@"Cell"];

		if (cell == nil)
		{
			cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:@"Cell"] autorelease];
		}

		cell.text = NSLocalizedString(@"Add task...", @"Add task cell text");
	}
	else
	{
		TaskCell *taskCell = (TaskCell *)[tableView dequeueReusableCellWithIdentifier:@"TaskCell"];

		if (taskCell == nil)
		{
			taskCell = [[[CellFactory cellFactory] createTaskCell] autorelease];
		}

		TaskList *list = [headers objectAtIndex:indexPath.section - (self.editing ? 1 : 0)];
		Task *task = [list taskAtIndex:indexPath.row];

		[taskCell setTask:task target:self action:@selector(onToggleTaskCompletion:)];

		cell = (UITableViewCell *)taskCell;
	}

    return cell;
}

- (UITableViewCellEditingStyle)tableView:(UITableView *)tableView editingStyleForRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (isBecomingEditable)
	{
		isBecomingEditable = NO;
		return UITableViewCellEditingStyleDelete;
	}

	return indexPath.section ? UITableViewCellEditingStyleDelete : UITableViewCellEditingStyleInsert;
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (indexPath.section == 0)
	{
		// XXXTODO: add task
	}
	else
	{
		Task *task = [[headers objectAtIndex:indexPath.section - 1] taskAtIndex:indexPath.row];
		
		if (task.status == STATUS_NEW)
		{
			// The desktop never head of this one, get rid of it
			[task delete];
		}
		else
		{
			[task setStatus:STATUS_DELETED];
			[task save];
		}

		if ([[headers objectAtIndex:indexPath.section - 1] count] == 1)
		{
			// The whole section is removed
			[headers removeObjectAtIndex:indexPath.section - 1];
			[self.tableView deleteSections:[NSIndexSet indexSetWithIndex:indexPath.section] withRowAnimation:UITableViewRowAnimationFade];
		}
		else
		{
			// The section stays, a row disappears
			[[headers objectAtIndex:indexPath.section - 1] reload];
			[self.tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationFade];
		}
	}
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (tapping && ([tapping compare:indexPath] == NSOrderedSame))
	{
		[self.tableView deselectRowAtIndexPath:tapping animated:NO];
		[tapping release];
		tapping = nil;

		return;
	}

	Task *task = [[headers objectAtIndex:indexPath.section - (self.editing ? 1 : 0)] taskAtIndex:indexPath.row];
	TaskDetailsController *ctrl = [[TaskDetailsController alloc] initWithTask:task];
	[self.navigationController pushViewController:ctrl animated:YES];
	[ctrl release];
}

@end

